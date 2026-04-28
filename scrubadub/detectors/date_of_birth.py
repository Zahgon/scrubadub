"""
This modules provides a detector for date of births.

The filter_type = contextual is simply looking for any detected dates that are more than 18 years
and date of birth has been mentioned within 2 previous lines.

Another option is to nuke all date of birth that is between 18 and 100 years.

Using 18+ years may not be suitable for all use cases; use with caution.
"""
import re
import logging
from dateparser.search import search_dates
from datetime import datetime

from typing import Optional, List, Generator

from scrubadub.detectors.catalogue import register_detector
from .base import Detector
from ..filth.base import Filth
from ..filth.date_of_birth import DateOfBirthFilth


@register_detector
class DateOfBirthDetector(Detector):
    """This detector aims to detect dates of birth in text.

    First all possible dates are found, then they are filtered to those that would result in people being between
    ``DateOfBirthFilth.min_age_years`` and ``DateOfBirthFilth.max_age_years``, which default to 18 and 100
    respectively.

    If ``require_context`` is True, we search for one of the possible ``context_words`` near the found date. We search
    up to ``context_before`` lines before the date and up to ``context_after`` lines after the date. The context that
    we search for are terms like `'birth'` or `'DoB'` to increase the likelihood that the date is indeed a date of
    birth. The context words can be set using the ``context_words`` parameter, which expects a list of strings.

    >>> import scrubadub, scrubadub.detectors.date_of_birth
    >>> DateOfBirthFilth.min_age_years = 12
    >>> scrubber = scrubadub.Scrubber(detector_list=[
    ...     scrubadub.detectors.date_of_birth.DateOfBirthDetector(),
    ... ])
    >>> scrubber.clean("I was born on 10-Nov-2008.")
    'I was born {{DATE_OF_BIRTH}}.'

    """
    name = 'date_of_birth'
    filth_cls = DateOfBirthFilth
    autoload = False

    context_words_language_map = {
        'en': ['birth', 'born', 'dob', 'd.o.b.'],
        'de': ['geburt', 'geboren', 'geb', 'geb.'],
    }

    def __init__(self, context_before: int = 2, context_after: int = 1, require_context: bool = True,
                 context_words: Optional[List[str]] = None, **kwargs):
        """Initialise the detector.

        :param context_before: The number of lines of context to search before the date
        :type context_before: int
        :param context_after: The number of lines of context to search after the date
        :type context_after: int
        :param require_context: Set to False if your dates of birth are not near words that provide context (such as
            "birth" or "DOB").
        :type require_context: bool
        :param context_words: A list of words that provide context related to dates of birth, such as the following:
            'birth', 'born', 'dob' or 'd.o.b.'.
        :type context_words: bool
        :param name: Overrides the default name of the :class:``Detector``
        :type name: str, optional
        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str, optional
        """
        super(DateOfBirthDetector, self).__init__(**kwargs)

        self.context_before = context_before
        self.context_after = context_after
        self.require_context = require_context

        try:
            self.context_words = self.context_words_language_map[self.language]
        except KeyError:
            raise ValueError("DateOfBirthDetector does not support language {}.".format(self.language))

        if context_words is not None:
            self.context_words = context_words

        self.context_words = [word.lower() for word in self.context_words]

    def iter_filth(self, text: str, document_name: Optional[str] = None) -> Generator[Filth, None, None]:
        """Search ``text`` for ``Filth`` and return a generator of ``Filth`` objects.

        :param text: The dirty text that this Detector should search
        :type text: str
        :param document_name: Name of the document this is being passed to this detector
        :type document_name: Optional[str]
        :return: The found Filth in the text
        :rtype: Generator[Filth]
        """
        pass

    @classmethod
    def supported_locale(cls, locale: str) -> bool:
        """Returns true if this ``Detector`` supports the given locale.

        :param locale: The locale of the documents in the format: 2 letter lower-case language code eg "en", "es".
        :type locale: str
        :return: ``True`` if the locale is supported, otherwise ``False``
        :rtype: bool
        """
        pass


__all__ = ['DateOfBirthDetector']
