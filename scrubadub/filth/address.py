import string
import random

from faker import Faker

from .base import Filth


class AddressFilth(Filth):
    type = 'address'

    @staticmethod
    def _randomise_seperators(address: str) -> str:
        pass

    @staticmethod
    def _randomise_street_number(address: str) -> str:
        pass

    @staticmethod
    def _randomise_postcode(address: str) -> str:
        pass

    @staticmethod
    def _randomise_country(address: str) -> str:
        pass

    @staticmethod
    def _randomise_building(address: str, faker: Faker) -> str:
        pass

    @staticmethod
    def _randomise_case(address: str) -> str:
        pass

    @staticmethod
    def generate(faker: Faker) -> str:
        """Generates an example of this ``Filth`` type, usually using the faker python library.

        :param faker: The ``Faker`` class from the ``faker`` library
        :type faker: Faker
        :return: An example of this ``Filth``
        :rtype: str
        """
        pass
