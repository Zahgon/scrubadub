import warnings
from faker import Faker
from typing import Optional, ClassVar, Pattern, List, Match

from .. import exceptions
from .. import utils


class Filth(object):
    """This is the base class for all ``Filth`` that is detected in dirty dirty
    text.
    """

    # this allows people to customize the output, especially for placeholder
    # text and identifier replacements
    prefix = u'{{'  # type: ClassVar[str]
    suffix = u'}}'  # type: ClassVar[str]

    # the `type` is used when filths are merged to come up with a sane label
    type = 'unknown'  # type: ClassVar[str]

    # the `lookup` is used to keep track of all of the different types of filth
    # that are encountered across all `Filth` types.
    lookup = utils.Lookup()

    # For backwards compatibility, but this is deprecated.
    regex = None  # type: Optional[Pattern[str]]

    def __init__(self, beg: Optional[int] = None, end: Optional[int] = None, text: Optional[str] = None,
                 match: Optional[Match] = None, detector_name: Optional[str] = None,
                 document_name: Optional[str] = None, replacement_string: Optional[str] = None,
                 locale: Optional[str] = None, **kwargs):

        self.beg = 0  # type: int
        self.end = 0  # type: int
        self.text = ''  # type: str
        self.match = None  # type: Optional[Match]

        if match is not None and isinstance(match, Match):
            self.beg = match.start()
            self.end = match.end()
            self.text = match.string[match.start():match.end()]
            self.match = match

        if beg is not None:
            self.beg = beg
        if end is not None:
            self.end = end
        if text is not None:
            self.text = text

        self.detector_name = detector_name  # type: Optional[str]
        self.document_name = document_name  # type: Optional[str]
        self.replacement_string = replacement_string  # type: Optional[str]
        self.locale = locale  # type: Optional[str]

        if self.beg >= self.end:
            raise ValueError(
                f"Creating invalid filth (self.beg >= self.end): {self}"
            )

    @property
    def placeholder(self) -> str:
        pass

    @property
    def identifier(self) -> str:
        # NOTE: this is not an efficient way to store this in memory. could
        # alternatively hash the type and text and do away with the overhead
        # bits of storing the tuple in the lookup
        pass

    def replace_with(self, replace_with: str = 'placeholder', **kwargs) -> str:
        pass

    def merge(self, other_filth: 'Filth') -> 'MergedFilth':
        pass

    def __repr__(self) -> str:
        return self._to_string()

    def _to_string(self, attributes: Optional[List[str]] = None) -> str:
        pass

    def __eq__(self, other) -> bool:
        """Only test equality on a subset of class attributes and some are optional"""
        match = True

        if not hasattr(other, 'beg') or not hasattr(other, 'end') or not hasattr(other, 'text'):
            raise TypeError("Unsupported comparison with a Filth and {}".format(type(other)))

        match &= (self.beg == other.beg)
        match &= (self.end == other.end)
        match &= (self.text == other.text)

        if hasattr(self, 'document_name') or hasattr(other, 'document_name'):
            match &= (self.document_name == other.document_name)
        if hasattr(self, 'detector_name') or hasattr(other, 'detector_name'):
            match &= (self.detector_name == other.detector_name)

        return match

    @staticmethod
    def generate(faker: Faker) -> str:
        """Generates an example of this ``Filth`` type, usually using the faker python library.

        :param faker: The ``Faker`` class from the ``faker`` library
        :type faker: Faker
        :return: An example of this ``Filth``
        :rtype: str
        """
        raise NotImplementedError("A generate() function has not been implemented for this Filth")

    def is_valid(self) -> bool:
        pass


class MergedFilth(Filth):
    """This class takes care of merging different types of filth"""

    def __init__(self, a_filth: Filth, b_filth: Filth):
        super(MergedFilth, self).__init__(
            beg=a_filth.beg,
            end=a_filth.end,
            text=a_filth.text,
            document_name=a_filth.document_name,
        )
        self.filths = [a_filth]
        self._update_content(b_filth)

    def _update_content(self, other_filth: Filth):
        """this updates the bounds, text and placeholder for the merged
        filth
        """
        pass

    @property
    def placeholder(self):
        pass

    def merge(self, other_filth: Filth) -> 'MergedFilth':
        """Be smart about merging filth in this case to avoid nesting merged
        filths.
        """
        pass

    def __repr__(self) -> str:
        return self._to_string(['filths'])


class RegexFilth(Filth):
    def __init__(self, *args, **kwargs):
        warnings.warn("Use of RegexFilth is depreciated, use Filth directly instead.", DeprecationWarning)
        super(RegexFilth, self).__init__(*args, **kwargs)
