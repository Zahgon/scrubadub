import re
import nltk
import textblob

from textblob.blob import BaseBlob
from textblob.en.taggers import PatternTagger

from typing import Optional, Generator

from scrubadub.detectors.catalogue import register_detector
from .base import RegexDetector
from ..filth import SkypeFilth, Filth

# BaseBlob uses NLTKTagger as a pos_tagger, but it works wrong
BaseBlob.pos_tagger = PatternTagger()


@register_detector
class SkypeDetector(RegexDetector):
    """Skype usernames tend to be used inline in dirty dirty text quite
    often but also appear as ``skype: {{SKYPE}}`` quite a bit. This method
    looks at words within ``word_radius`` words of "skype" for things that
    appear to be misspelled or have punctuation in them as a means to
    identify skype usernames.

    Default ``word_radius`` is 10, corresponding with the rough scale of
    half of a sentence before or after the word "skype" is used. Increasing
    the ``word_radius`` will increase the false positive rate and
    decreasing the ``word_radius`` will increase the false negative rate.
    """
    filth_cls = SkypeFilth
    name = 'skype'
    autoload = False

    word_radius = 10

    # these two regular expressions are used to validate a skype usernames.
    # _TOKEN is the core regular expression that is used to chunk text into
    # tokens to make sure all valid skype usernames are considered the same
    # token. Importantly, the word "skype" must pass the _SKYPE regex.
    # SKYPE_TOKEN is used to tokenize text and SKYPE_USERNAME is the same thing
    # but with the 6-32 character limit imposed on the username. adapted from
    # http://bit.ly/1FQs1hD
    _SKYPE = r'[a-zA-Z][a-zA-Z0-9_\-\,\.]'
    SKYPE_TOKEN = _SKYPE + '+'
    SKYPE_USERNAME = re.compile(_SKYPE+'{5,31}')

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
