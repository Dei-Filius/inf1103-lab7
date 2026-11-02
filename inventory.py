from product import Product


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
