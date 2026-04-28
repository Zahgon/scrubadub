import random
import datetime
import dateparser
from faker import Faker

from .base import Filth


class DateOfBirthFilth(Filth):
    type = 'date_of_birth'
    min_age_years = 18
    max_age_years = 100

    @staticmethod
    def generate(faker: Faker) -> str:
        """Generates an example of this ``Filth`` type, usually using the faker python library.

        :param faker: The ``Faker`` class from the ``faker`` library
        :type faker: Faker
        :return: An example of this ``Filth``
        :rtype: str
        """
        pass

    def is_valid(self) -> bool:
        """Check to see if the found filth is valid."""
        pass
