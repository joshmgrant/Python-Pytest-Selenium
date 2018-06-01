import pytest
from os import environ

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.remote_connection import RemoteConnection


sauce_options = {
    "seleniumVersion": "3.11.0",
    "build": "Pytest W3C POC"
}

options = [
    {
        "platformName": "Windows 10",
        "browserName": "MicrosoftEdge",
        "browserVersion": "14.14393", 
        "sauce:options": sauce_options
    }, {
        "platformName": "Windows 10",
        "browserName": "firefox",
        "browserVersion": "49.0",
        "sauce:options": sauce_options
    }, {
        "platformName": "Windows 7",
        "browserName": "internet explorer",
        "browserVersion": "11.0",
        "sauce:options": sauce_options
    }, {
        "platformName": "OS X 10.12",
        "browserName": "safari",
        "browserVersion": "11.0",
        "sauce:options": sauce_options
    }]

def pytest_generate_tests(metafunc):
    if 'driver' in metafunc.fixturenames:
        metafunc.parametrize('browser_config',
                             options,
                             ids=_generate_param_ids('broswerConfig', options),
                             scope='function')


def _generate_param_ids(name, values):
    return [("<%s:%s>" % (name, value)).replace('.', '_') for value in values]


@pytest.yield_fixture(scope='function')
def driver(request, browser_config):
    # if the assignment below does not make sense to you please read up on object assignments.
    # The point is to make a copy and not mess with the original test spec.
    browser_options = browser_config.copy()
    test_name = request.node.name
    username = environ.get('SAUCE_USERNAME', None)
    access_key = environ.get('SAUCE_ACCESS_KEY', None)

    selenium_endpoint = "http://{}:{}@ondemand.saucelabs.com/wd/hub".format(username, access_key)
    browser_options['sauce:options']['build'] = "Python W3C"
    browser_options['sauce:options']['name'] = test_name

    executor = RemoteConnection(selenium_endpoint, resolve_ip=False)
    browser = webdriver.Remote(
        command_executor=executor,
        desired_capabilities=browser_options
    )

    # This is specifically for SauceLabs plugin.
    # In case test fails after selenium session creation having this here will help track it down.
    # creates one file per test non ideal but xdist is awful
    if browser is not None:
        with open("%s.testlog" % browser.session_id, 'w') as f:
            f.write("SauceOnDemandSessionID=%s job-name=%s\n" % (browser.session_id, test_name))
    else:
        raise WebDriverException("Never created!")

    yield browser
    # Teardown starts here
    # report results
    try:
        browser.execute_script("sauce:job-result=%s" % str(not request.node.rep_call.failed).lower())
        browser.quit()
    except WebDriverException:
        # we can ignore the exceptions of WebDriverException type -> We're done with tests.
        print('Warning: The driver failed to quit properly. Check test and server side logs.')


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # this sets the result as a test attribute for SauceLabs reporting.
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set an report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)
