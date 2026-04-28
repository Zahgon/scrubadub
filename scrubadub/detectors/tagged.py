import re
import sys
import copy

from typing import Optional, List, Generator

from scrubadub.detectors.catalogue import register_detector
from .base import Detector
from ..filth.base import Filth
from ..filth.tagged import TaggedEvaluationFilth

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict

KnownFilthItem = TypedDict(
    'KnownFilthItem',
    {
        'match': str,
        'match_end': str,
        'limit': int,
        'ignore_case': bool,
        'ignore_whitespace': bool,
        'ignore_partial_word_matches': bool,
        'filth_type': str
    },
    total=False,
)


@register_detector
class TaggedEvaluationFilthDetector(Detector):
    """Use this ``Detector`` to find tag filth as true ``Filth``. This is useful when you want evaluate the
    effectiveness of a Detector using Filth that has been selected by a human.

    Results from this detector are used as the "truth" against which the other detectos are compared. This is done in
    ``scrubadub.comparison.get_filth_classification_report`` where the detecton accuracies are calculated.

    An example of how to use this detector is given below:

    >>> import scrubadub, scrubadub.comparison, scrubadub.detectors.text_blob
    >>> scrubber = scrubadub.Scrubber(detector_list=[
    ...     scrubadub.detectors.text_blob.TextBlobNameDetector(name='name_detector'),
    ...     scrubadub.detectors.TaggedEvaluationFilthDetector([
    ...         {'match': 'Tom', 'filth_type': 'name'},
    ...         {'match': 'tom@example.com', 'filth_type': 'email'},
    ...     ]),
    ... ])
    >>> filth_list = list(scrubber.iter_filth("Hello I am Tom"))
    >>> print(scrubadub.comparison.get_filth_classification_report(filth_list))
    filth    detector         locale      precision    recall  f1-score   support
    <BLANKLINE>
    name     name_detector    en_US            1.00      1.00      1.00         1
    <BLANKLINE>
                                accuracy                           1.00         1
                               macro avg       1.00      1.00      1.00         1
                            weighted avg       1.00      1.00      1.00         1
    <BLANKLINE>

    This detector takes a list of dictonaires (reffered to as known filth items). These specify what to look for in
    the text to label as tagged filth. The dictionary should contain the following keys:

        * ``match`` (`str`) - a string value that will be searched for in the text
        * ``filth_type`` (`str`) - a string value that indicates the type of Filth, should be set to ``Filth.name``.
          An example of these could be 'name' or 'phone' for name and phone filths respectively.

    The known filth item dictionary may also optionally contain:

        * ``match_end`` (`str`) - if specified will search for Filth starting with the value of match and ending with
          the value of ``match_end``
        * ``limit`` (`int`) - an integer describing the maximum number of characters between match and match_end,
          defaults to 150
        * ``ignore_case`` (`bool`) - Ignore case when searching for the tagged filth
        * ``ignore_whitespace`` (`bool`) - Ignore whitespace when matching ("asd qwe" can also match "asd\\\\nqwe")
        * ``ignore_partial_word_matches`` (`bool`) - Ignore matches that are only partial words (if you're looking
          for "Eve", this flag ensure it wont match "Evening")

    Examples of this:

        * ``{'match': 'aaa', 'filth_type': 'name'}`` - will search for an exact match to aaa and return it as a
          ``NameFilth``
        * ``{'match': 'aaa', 'match_end': 'zzz', 'filth_type': 'name'}`` - will search for `aaa` followed by up to 150
          characters followed by `zzz`, which would match both `aaabbbzzz` and `aaazzz`.
        * ``{'match': '012345', 'filth_type': 'phone', 'ignore_partial_word_matches': True}`` - will search for an
          exact match to 012345, ignoring any partial matches and return it as a ``PhoneFilth``

    This detector is not enabled by default (since you need to supply a list of known filths) and so you must always
    add it to your scrubber with a ``scrubber.add_detector(detector)`` call or by adding it to the ``detector_list``
    inialising a ``Scrubber``.
    """

    filth_cls = TaggedEvaluationFilth
    name = 'tagged'
    autoload = False

    def __init__(self, known_filth_items: List[KnownFilthItem], **kwargs):
        """Initialise the ``Detector``.

        :param known_filth_items: A list of dictionaries that describe items to be searched for in the dirty text.
            The keys `match` and `filth_type` are required, which give the text to be searched for and the type of
            filth that the `match` string represents.
            See the class docstring for further details of available flags in this dictionary.
        :type known_filth_items: list of dicts
        :param tagged_filth: Whether the filth has been tagged and should be used as truth when calculating filth
            finding accuracies.
        :type tagged_filth: bool, default True
        :param name: Overrides the default name of the :class:``Detector``
        :type name: str, optional
        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str, optional
        """
        super().__init__(**kwargs)

        for item in known_filth_items:
            if 'match' not in item or 'filth_type' not in item:
                raise KeyError("Each known filth item (dict) needs both keys 'match' and 'filth_type'.")
            if not isinstance(item['match'], str):
                raise ValueError("The value of 'match' in each KnownItem should be a string. "
                                 "Current value: " + item['match'].__repr__())
            if not isinstance(item['filth_type'], str):
                raise ValueError("The value of 'filth_type' in each KnownItem should be a string. "
                                 "Current value: " + item['filth_type'].__repr__())
            item['match'] = item['match'].strip()
            item['filth_type'] = item['filth_type'].strip()
            if 'match_end' in item:
                if not isinstance(item['match_end'], str):
                    raise ValueError("The value of 'match_end' in each KnownItem should be a string. "
                                     "Current value: " + item['match_end'].__repr__())
                item['match_end'] = item['match_end'].strip()

            for key in item.keys():
                if key not in ['match', 'match_end', 'limit', 'filth_type', 'ignore_case', 'ignore_whitespace',
                               'ignore_partial_word_matches']:
                    raise KeyError("Unexpected key '{}' in the known filth item.".format(key))

        self._known_filth_items = self.dedup_dicts(known_filth_items)

    @staticmethod
    def dedup_dicts(known_filth_items: List[KnownFilthItem]) -> List[KnownFilthItem]:
        # It would be nicer to do this with a set, but sets and dictionaries dont work well together, plus this way
        # we get to keep the typing info associated to these dicts.
        pass

    def create_filth(
            self, start_location: int, end_location: int, text: str, comparison_type: Optional[str],
            detector_name: str, document_name: Optional[str], locale: str
    ) -> Filth:
        pass

    def _find_all(
            self,
            text: str,
            substr: str,
            comparison_type: Optional[str] = None,
            document_name: Optional[str] = None,
            ignore_case: bool = False,
            ignore_whitespace: bool = False,
            ignore_partial_word_matches: bool = False,
    ) -> Generator[Filth, None, None]:
        """Yield filth for each match to substr in text."""
        pass

    def _find_all_between(
            self,
            text: str,
            substr_start: str,
            substr_end: str,
            limit: int = 150,
            comparison_type: Optional[str] = None,
            document_name: Optional[str] = None,
            ignore_case: bool = False,
            ignore_whitespace: bool = False,
            ignore_partial_word_matches: bool = False,
    ) -> Generator[Filth, None, None]:
        """Yield filth for text between (and including)
        substr_start and substr_end, but only if the text
        between the two is less than limit characters.
        """
        pass

    def iter_filth(
            self,
            text: str,
            document_name: Optional[str] = None
    ) -> Generator[Filth, None, None]:
        """Yields discovered filth in the provided ``text``.

        :param text: The dirty text to clean.
        :type text: str
        :param document_name: The name of the document to clean.
        :type document_name: str, optional
        :return: An iterator to the discovered :class:`Filth`
        :rtype: Iterator[:class:`Filth`]
        """
        pass
