import re
import textblob

from textblob.blob import BaseBlob
from textblob.en.taggers import PatternTagger

from typing import Optional, Generator

from scrubadub.detectors.catalogue import register_detector
from .base import RegexDetector
from ..filth import NameFilth, Filth
from ..utils import CanonicalStringSet

# BaseBlob uses NLTKTagger as a pos_tagger, but it works wrong
BaseBlob.pos_tagger = PatternTagger()


@register_detector
class TextBlobNameDetector(RegexDetector):
    """Use part of speech tagging from textblob to clean proper nouns out of the dirty dirty
    ``text``. Disallow particular nouns by adding them to the ``NameDetector.disallowed_nouns`` set.
    """
    filth_cls = NameFilth
    name = 'text_blob_name'
    autoload = False

    disallowed_nouns = CanonicalStringSet(["skype"])

    def iter_filth(self, text, document_name: Optional[str] = None) -> Generator[Filth, None, None]:
        """Yields discovered filth in the provided ``text``.

        :param text: The dirty text to clean.
        :type text: str
        :param document_name: The name of the document to clean.
        :type document_name: str, optional
        :return: An iterator to the discovered :class:`Filth`
        :rtype: Iterator[:class:`Filth`]
        """
        pass

    @classmethod
    def supported_locale(cls, locale: str) -> bool:
        """Returns true if this ``Detector`` supports the given locale.

        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str
        :return: ``True`` if the locale is supported, otherwise ``False``
        :rtype: bool
        """
        pass
