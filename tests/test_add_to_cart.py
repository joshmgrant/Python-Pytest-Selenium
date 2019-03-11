import pytest


def test_add_one_item(driver):
    driver.get('http://www.saucedemo.com/inventory.html')
    driver.find_element_by_class_name('add-to-cart-button').click()

    assert driver.find_element_by_class_name('shopping_cart_badge').text == '1'

def test_add_two_items(driver):
    driver.get('https://www.saucedemo.com/inventory.html')
    driver.find_element_by_class_name('add-to-cart-button').click()
    driver.find_element_by_class_name('add-to-cart-button').click()

    assert driver.find_element_by_class_name('shopping_cart_badge').text == '2'

