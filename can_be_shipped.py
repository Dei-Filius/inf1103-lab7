from abc import ABC, abstractmethod


class CanBeShipped(ABC):
    """
    Interface for shippable products.
    """

    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        pass
