import pprint

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "selenium_iphone_project.settings")
django.setup()

from parser_app.models import Product, ProductPhoto, ProductCharacteristic


def parse_price(text: str) -> float:
    clean = (
        text.replace("₴", "")
            .replace("грн", "")
            .replace("ГРН", "")
            .replace(" ", "")
            .strip()
    )
    try:
        return float(clean)
    except:
        return None


def scrape_product(driver) -> Product:
    url = driver.current_url

    wait = WebDriverWait(driver, 10)
    # Product name
    name_el = driver.find_element(By.XPATH, "//h1[@class='main-title']") #
    full_name = name_el.text.strip()

    # Color and memory from the name
    color = None
    memory = None
    parts = full_name.split()

    for p in parts:
        if "gb" in p.lower():
            memory = p.upper()
        if p.lower() in ["black", "white", "blue", "gold", "titanium", "green"]:
            color = p.capitalize()


    # Regular price
    price_regular_el = driver.find_element(
        By.XPATH,
        "//div[@class='price-wrapper']"
    )
    price_regular = parse_price(price_regular_el.text)

    # If there is a discount
    try:
        price_discount_el = driver.find_element(
            By.XPATH,
            "//span[@class='red-price']"
        )
        price_discount = parse_price(price_discount_el.text)
        print(f"Price discount: {price_discount}")
    except:
        price_discount = None


    # product code
    try:
        code_el = driver.find_element(By.XPATH, "//div[@class='br-body br-body-product']//div//span[@class='br-pr-code-val']")
        product_code = code_el.text.strip()
    except:
        product_code = None

    # Amount of reviews
    try:
        reviews_el = driver.find_element(
            By.XPATH,
            "//a[@class='scroll-to-element']//span"
        )
        reviews_count = int(
            reviews_el.text
                .replace("Відгуки (", "")
                .replace(")", "")
                .strip()
        )
    except:
        reviews_count = 0

    characteristics_button = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//div[@class='br-pr-tblock br-pr-chr-wrap']//button[@class='br-prs-button']"
        ))
    )
    characteristics_button.click()

    # Creating a list of characteristics
    characteristics = {}

    characteristic_blocks = driver.find_elements(By.XPATH, "(//div//div//div[@class='br-pr-chr-item']//div//span)")

    for i in range(0, len(characteristic_blocks), 2):
        name = characteristic_blocks[i].text.strip()
        value = characteristic_blocks[i + 1].text.strip().replace(",  ", ", ")
        characteristics[name] = value


    # From characteristics storing the diagonal of screen, screen resolution,manufacturer
    screen_diagonal = characteristics.get("Діагональ екрану")
    screen_resolution = characteristics.get("Роздільна здатність екрану")
    manufacturer = characteristics.get("Виробник")

    # Creating product
    product = Product.objects.create(
        url=url,
        full_name=full_name,
        color=color,
        memory=memory,
        manufacturer=manufacturer,
        price_regular=price_regular,
        price_discount=price_discount,
        product_code=product_code,
        reviews_count=reviews_count,
        screen_diagonal=screen_diagonal,
        screen_resolution=screen_resolution,
    )

    # Storing characteristics
    for name, value in characteristics.items():
        if name and value:
            ProductCharacteristic.objects.create(
                product=product,
                name=name,
                value=value
            )

    # Storing photos
    photo_urls = []

    main_imgs = driver.find_elements(By.CSS_SELECTOR, "img.br-main-img")
    preview_imgs = driver.find_elements(By.CSS_SELECTOR, "img.br-pr-img")

    all_imgs = main_imgs + preview_imgs

    for img in all_imgs:
        src = img.get_attribute("src")
        if not src:
            continue

        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = "https://brain.com.ua" + src

        photo_urls.append(src)

    for url in photo_urls:
        ProductPhoto.objects.create(product=product, url=url)

    print(f"Created product: {product.full_name}")
    print(f"Color: {color}")
    print(f"Memory: {memory}")
    print(f"Manufacturer: {manufacturer}")
    print(f"Regular price: {price_regular}\nDiscount price: {price_discount}")
    print(f"Price code: {product_code}")
    print(f"Reviews amount: {reviews_count}")
    print(f"Screen diagonal: {screen_diagonal}")
    print(f"Screen resolution: {screen_resolution}")

    pprint.pprint(characteristics)

    return product

if __name__ == "__main__":
    scrape_product("https://brain.com.ua/ukr/Mobilniy_telefon_Apple_iPhone_16_Pro_Max_256GB_Black_Titanium-p1145443.html")
