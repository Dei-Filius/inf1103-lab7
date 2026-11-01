from abc import ABC, abstractmethod
import json
from pathlib import Path

INVENTORY_FILE_PATH: str = "data/inventory.json"
inventory_file = Path(INVENTORY_FILE_PATH)

SHIPPING_RATE = 4.0


class Product(ABC):
    """
    Abstract Product Class.
    """
    def __init__(self, product_id: str, name: str, price: float, stock: int):
        self.__product_id = product_id
        self.__name = name
        self.__price = price
        self.__stock = stock

    def update_stock(self, stock: int) -> None:
        if stock < 0:
            raise ValueError("stock cannot be negative")

        self.__stock = stock

    def display_information(self) -> None:
        print(f"ID: {self.__product_id}", end=" | ")
        print(f"Name: {self.__name}", end=" | ")
        print(f"Price: ${self.__price:.2f}", end=" | ")
        print(f"Stock: {self.__stock}")

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        pass

    def to_dict(self) -> dict:
        return {
            "id": self.__product_id,
            "name": self.__name,
            "price": self.__price,
            "stock": self.__stock,
        }

    @property
    def product_id(self) -> str:
        return self.__product_id


class CanBeShipped(ABC):
    """
    Interface for shippable products.
    """
    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        pass


class PhysicalProduct(Product, CanBeShipped):
    def __init__(
        self, product_id: str, name: str, price: float, stock: int, weight: int
    ):
        super().__init__(product_id, name, price, stock)
        self.__weight = weight

    def display_information(self) -> None:
        super().display_information()
        print(f"*Weight: {self.__weight}")

    def calculate_shipping_cost(self) -> float:
        return self.__weight * SHIPPING_RATE

    def get_fulfilment_info(self) -> str:
        return "Require physical shipping"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["type"] = "PHYSICAL"
        return data


class DigitalProduct(Product):
    def __init__(
        self, product_id: str, name: str, price: float, stock: int, download_size: int
    ):
        super().__init__(product_id, name, price, stock)
        self.__download_size = download_size

    def display_information(self) -> None:
        super().display_information()
        print(f"*Download Size(MB): {self.__download_size}")

    def get_fulfilment_info(self):
        return "Delievered digitally"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["type"] = "DIGITAL"
        return data


class Inventory:
    """
    Collection of Products.
    """
    def __init__(self) -> None:
        self.__products: dict[str, Product] = {}

    def add_product(self, product: Product) -> None:
        self.__products[product.product_id] = product

    def search_product(self, product_id: str) -> Product | None:
        return self.__products.get(product_id.upper())

    def display_all(self) -> None:
        print()
        print("Current Inventory")
        print("------------------------------------------------")
        if len(self) > 0:
            for _, product in self.__products.items():
                product.display_information()
        else:
            print("Nothing...")
        print("------------------------------------------------")

    def to_list(self) -> list:
        return [product.to_dict() for _, product in self.__products.items()]

    def __len__(self) -> int:
        return len(self.__products)


def load_inventory() -> Inventory:
    print()
    print("Loading inventory...")
    inventory = Inventory()
    try:
        with inventory_file.open("r") as file:
            for product in json.load(file):
                inventory.add_product(
                    Product(
                        product["id"],
                        product["name"],
                        product["price"],
                        product["stock"],
                    )
                )
    except FileNotFoundError:
        inventory_file.parent.mkdir(parents=True, exist_ok=True)
        inventory_file.touch()
    except json.JSONDecodeError:
        print("Inventory file might be corrupted.")
        print("Exiting...")
        exit()
    return inventory


def save_inventory(inventory: Inventory) -> None:
    print()
    print("Saving inventory...")
    with inventory_file.open("w") as file:
        json.dump(inventory.to_list(), file, indent=4)
    print("Inventory saved successfully to", INVENTORY_FILE_PATH)


def add_product(inventory: Inventory) -> None:
    print()
    print("Add New Product")
    product_id = get_product_id_input()

    if inventory.search_product(product_id):
        print("Product already exists.")
        return

    name = get_str_input("Product Name: ").strip()
    price = get_price_input("Price (omit $ sign): ")
    stock = get_int_input("Stock Quantity: ", 0)
    inventory.add_product(Product(product_id, name, price, stock))
    print("Product added successfully!")


def update_stock(inventory: Inventory) -> None:
    print()
    print("Update Stock")
    product_id = get_product_id_input()
    product = inventory.search_product(product_id)

    if product is None:
        print("This Product is not in Inventory.")
        return

    print("Product Found!")
    print("------------------------------------------------")
    product.display_information()
    print("------------------------------------------------")

    stock = get_int_input("New Stock Quantity: ", 0)
    product.update_stock(stock)

    print()
    print("Product Updated!")
    print("------------------------------------------------")
    product.display_information()
    print("------------------------------------------------")


def search_product(inventory: Inventory) -> None:
    print()
    product_id = get_product_id_input()
    product = inventory.search_product(product_id)
    if product is None:
        print("This Product is not in Inventory.")
        return

    print("Product Found!")
    print("------------------------------------------------")
    product.display_information()
    print("------------------------------------------------")


def exit_app(inventory: Inventory):
    save_inventory(inventory)
    print()
    print("Thank you for using Inventory Management System.")
    print("Program terminated.")
    exit()


def get_str_input(msg: str) -> str:
    """
    Get non-empty string from user
    """
    while True:
        user_input = input(msg)
        if user_input:
            return user_input
        print("Invalid. Input is empty. Try again.")


def get_int_input(msg: str, minimum=None, maximum=None) -> int:
    """
    get int from user within min max value.
    """
    while True:
        try:
            user_input = int(input(msg))
            if minimum is not None:
                if user_input < minimum:
                    raise ValueError()
            if maximum is not None:
                if user_input > maximum:
                    raise ValueError()
            return user_input
        except ValueError:
            print("Invalid. Try again.")


def get_price_input(msg: str) -> float:
    """
    Get valid price from user, price >=0
    """
    while True:
        try:
            user_input = round(float(input(msg)), 2)
            if user_input < 0:
                raise ValueError()
            return user_input
        except ValueError:
            print("Invalid. Try again.")


def get_product_id_input() -> str:
    """
    Get valid Product ID from user, starts with P then followed by digits.
    """
    while True:
        try:
            user_input = input("Product ID: ").strip().upper()
            if not (user_input.startswith("P") or user_input[1:].isdigit()):
                raise ValueError()
            return user_input
        except ValueError:
            print("Invalid Product ID. Try again.")


def display_menu(menu: list[dict]) -> None:
    print()
    print("----------- MENU -----------")
    for i, page in enumerate(menu, 1):
        print(f"{i}. {page["text"]}")
    print("----------------------------")


def main() -> None:
    try:
        inventory = load_inventory()

        menu: list[dict] = [
            {"text": "Display All Products", "action": lambda: inventory.display_all()},
            {"text": "Add Product", "action": lambda: add_product(inventory)},
            {"text": "Update Stock", "action": lambda: update_stock(inventory)},
            {"text": "Search Product", "action": lambda: search_product(inventory)},
            {"text": "Save Inventory", "action": lambda: save_inventory(inventory)},
            {"text": "Exit", "action": lambda: exit_app(inventory)},
        ]

        print("""
========================================
INVENTORY MANAGEMENT SYSTEM
========================================
        """)
        while True:
            try:
                display_menu(menu)
                option = get_int_input("Enter option: ", 0, len(menu))
                try:
                    menu[option - 1]["action"]()
                except KeyboardInterrupt:
                    continue
            except KeyboardInterrupt:
                exit_app(inventory)
                break

    except json.decoder.JSONDecodeError:
        print(f"Error decoding json file {INVENTORY_FILE_PATH}")
        print("Exiting...")
    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == "__main__":
    main()
