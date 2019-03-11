import pytest


def test_standard_user(driver):
    driver.get("http://www.saucedemo.com")

    driver.find_element_by_id('user-name').send_keys('standard_user')
    driver.find_element_by_id('password').send_keys('secret_sauce')
    driver.find_element_by_css_selector('.login-button').click()

    assert "/inventory.html" in driver.current_url
    