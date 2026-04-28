import re
import locale as locale_module

from typing import Optional, Tuple, List

try:
    unicode  # type: ignore  # tell mypy to ignore the fact that this doesnt exist in python3
except NameError:
    basestring = str  # Compatibility for Python 2 and 3


class CanonicalStringSet(set):
    """Just like a set, except it makes sure that all elements are lower case
    strings.
    """

    def _cast_as_lower(self, x):
        pass

    def __init__(self, *elements):
        super(CanonicalStringSet, self).__init__()
        if elements:
            self.update(*elements)

    def __contains__(self, element):
        return super(CanonicalStringSet, self).__contains__(
            self._cast_as_lower(element)
        )

    def add(self, element):
        pass

    def update(self, elements):
        pass

    def remove(self, element):
        pass

    def discard(self, element):
        pass


class Lookup(object):
    """The Lookup object is used to create an in-memory reference table to
    create unique identifiers for ``Filth`` that is encountered.
    """

    def __init__(self):
        self.table = {}

    def __getitem__(self, key):
        try:
            return self.table[key]
        except KeyError:
            self.table[key] = len(self.table)
            return self.table[key]


def locale_transform(locale: str) -> str:
    """Normalise the locale string, e.g. 'fr' -> 'fr_FR'.

    :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                   underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
    :type locale: str
    :return: The normalised locale string
    :rtype: str
    """
    pass


def locale_split(locale: str) -> Tuple[Optional[str], Optional[str]]:
    """Split the locale string into the language and region.

    :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                   underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
    :type locale: str
    :return: The two-letter language code and the two-letter region code in a tuple.
    :rtype: tuple, (str, str)
    """
    pass


class ToStringMixin(object):
    def _to_string(self, attributes: List[str]) -> str:
        pass
