import re
import copy
import random
import itertools

from faker import Faker

from . import filth as filth_module
from .filth import Filth
from .detectors.tagged import KnownFilthItem

from typing import List, Dict, Union, Optional, Tuple, Callable, Iterable, Type, Set
import numpy as np
import pandas as pd
import sklearn.metrics

# I was originally thinking of building this into the Filth system, but they serve subtlly different purposes:
#   * Filths need to be merged by text location so that replacements can be made
#   * TextPostions need to be merged by text location, but seperated by type so that we an correclty count them
from .utils import ToStringMixin

Grouping = Dict[str, str]
GroupingFunction = Callable[[Filth], Grouping]


class TextPosition(ToStringMixin):
    def __init__(self, filth: Filth, grouping_function: GroupingFunction):
        self.beg = filth.beg
        self.end = filth.end
        self.detected = set()  # type: Set[Tuple[str, ...]]
        self.tagged = set()  # type: Set[Tuple[str, ...]]
        self.document_name = str(filth.document_name or '')  # type: str

        if isinstance(filth, filth_module.TaggedEvaluationFilth):
            self.tagged.add(tuple(grouping_function(filth).values()))
        else:
            self.detected.add(tuple(grouping_function(filth).values()))

    @staticmethod
    def sort_key(position: 'TextPosition') -> Tuple[str, int, int]:
        pass

    def merge(self, other: 'TextPosition') -> 'TextPosition':
        pass

    def __repr__(self) -> str:
        return self._to_string(['beg', 'end', 'tagged', 'detected', 'document_name', ])

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class FilthTypePositions(ToStringMixin, object):
    def __init__(self, grouping_function: GroupingFunction, filth_type: str):
        self.positions = []  # type: List[TextPosition]
        self.filth_type = filth_type
        self.grouping_function = grouping_function
        self.column_names = None  # type: Optional[List[str]]

    def __repr__(self) -> str:
        return self._to_string(['filth_type', 'positions', ])

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def add_filth(self, filth: Filth):
        pass

    @staticmethod
    def _merge_position_list(position_list: List[TextPosition]) -> List[TextPosition]:
        pass

    def merge_positions(self):
        pass

    def get_counts(self) -> pd.DataFrame:
        pass


class FilthGrouper(ToStringMixin, object):
    def __init__(self, filth_types: Optional[List[str]] = None, grouping_function: Optional[GroupingFunction] = None,
                 combine_detectors: bool = False, groupby_documents: bool = False):
        self.types = {}  # type: Dict[str, FilthTypePositions]
        self.combine_detectors = combine_detectors
        self.groupby_documents = groupby_documents
        self.filth_types = filth_types

        if grouping_function is None:
            if self.combine_detectors and self.groupby_documents:
                self.grouping_function = FilthGrouper.grouping_combined_bydoc  # type: GroupingFunction
            elif self.combine_detectors and not self.groupby_documents:
                self.grouping_function = FilthGrouper.grouping_combined
            elif not self.combine_detectors and self.groupby_documents:
                self.grouping_function = FilthGrouper.grouping_default_bydoc
            else:
                self.grouping_function = FilthGrouper.grouping_default
        else:
            self.grouping_function = grouping_function

    def __repr__(self) -> str:
        return self._to_string(['combine_detectors', 'filth_types', 'types', ])

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @staticmethod
    def grouping_default(filth: Filth) -> Grouping:
        pass

    @staticmethod
    def grouping_default_bydoc(filth: Filth) -> Grouping:
        pass

    @staticmethod
    def grouping_combined(filth: Filth) -> Grouping:
        pass

    @staticmethod
    def grouping_combined_bydoc(filth: Filth) -> Grouping:
        pass

    def merge_positions(self):
        pass

    def add_filths(self, filth_list: List[Filth]):
        pass

    @classmethod
    def from_filth_list(
            cls, filth_list: List[Filth], filth_types: Optional[List[str]] = None,
            combine_detectors: bool = False, groupby_documents: bool = False,
            grouping_function: Optional[GroupingFunction] = None
    ) -> 'FilthGrouper':
        pass

    def expand_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def get_counts(self, expand_missing: bool = False) -> pd.DataFrame:
        pass


def get_filth_classification_report(
        filth_list: List[Filth],
        combine_detectors: bool = False,
        groupby_documents: bool = False,
        output_dict: bool = False,
) -> Optional[Union[str, Dict[str, float]]]:
    """Evaluates the performance of detectors using KnownFilth.

    An example of using this is shown below:

    .. code:: pycon

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

    :param filth_list: The list of detected filth
    :type filth_list: A list of `Filth` objects
    :param combine_detectors: Combine performance of all detectors for the same filth/locale
    :type combine_detectors: bool, optional
    :param groupby_documents: Show performance for each file individually
    :type groupby_documents: bool, optional
    :param output_dict: Return the report in JSON format, defautls to False
    :type output_dict: bool, optional
    :return: The report in JSON (a `dict`) or in plain text
    :rtype: `str` or `dict`
    """
    pass


def get_filth_dataframe(filth_list: List[Filth]) -> pd.DataFrame:
    """Produces a pandas `DataFrame` to allow debugging and improving detectors.

    An example of using this is shown below:

    .. code:: pycon

        >>> import scrubadub, scrubadub.comparison, scrubadub.detectors.text_blob
        >>> scrubber = scrubadub.Scrubber(detector_list=[
        ...     scrubadub.detectors.text_blob.TextBlobNameDetector(name='name_detector'),
        ...     scrubadub.detectors.TaggedEvaluationFilthDetector([
        ...         {'match': 'Tom', 'filth_type': 'name'},
        ...         {'match': 'tom@example.com', 'filth_type': 'email'},
        ...     ]),
        ... ])
        >>> filth_list = list(scrubber.iter_filth("Hello I am Tom"))
        >>> with pd.option_context("display.max_columns", 20):
        ...     print(scrubadub.comparison.get_filth_dataframe(filth_list))  # doctest: +NORMALIZE_WHITESPACE
           group_id  filth_id filth_type  detector_name document_name text  beg  end  \\
        0         0         0       name  name_detector          None  Tom   11   14
        <BLANKLINE>
          locale  known_filth comparison_type known_text  known_beg  known_end  \\
        0  en_US         True             NaN        Tom         11         14
        <BLANKLINE>
          known_comparison_type  exact_match  partial_match  true_positive  \\
        0                  name         True           True           True
        <BLANKLINE>
           false_positive  false_negative
        0           False           False

    :param filth_list: The list of detected filth
    :type filth_list: A list of `Filth` objects
    :return: A `pd.DataFrame` containing infomatoin about the detected `Filth`
    :rtype: `pd.DataFrame`

    """
    pass


def make_fake_document(
        paragraphs: int = 20, locale: str = 'en_US', seed: Optional[int] = None, faker: Optional[Faker] = None,
        filth_types: Optional[List[str]] = None, fake_text_function: Optional[Callable[..., str]] = None,
        additional_filth_types: Optional[Iterable[Type[Filth]]] = None,
) -> Tuple[str, List[KnownFilthItem]]:
    """Creates a fake document containing `Filth` that needs to be removed. Also returns the list of known filth
    items that are needed by the `TaggedEvaluationFilthDetector`\\ .

    An example of using this is shown below:

    .. code:: pycon

        >>> import scrubadub, scrubadub.comparison
        >>> document, known_filth_items = scrubadub.comparison.make_fake_document(paragraphs=1, seed=1)
        >>> scrubber = scrubadub.Scrubber()
        >>> scrubber.add_detector(scrubadub.detectors.TaggedEvaluationFilthDetector(
        ...     known_filth_items=known_filth_items
        ... ))
        >>> filth_list = list(scrubber.iter_filth(document))
        >>> print(scrubadub.comparison.get_filth_classification_report(filth_list))
        filth    detector    locale      precision    recall  f1-score   support
        <BLANKLINE>
        email    email       en_US            1.00      1.00      1.00         2
        url      url         en_US            1.00      1.00      1.00         1
        <BLANKLINE>
                              micro avg       1.00      1.00      1.00         3
                              macro avg       1.00      1.00      1.00         3
                           weighted avg       1.00      1.00      1.00         3
                            samples avg       1.00      1.00      1.00         3
        <BLANKLINE>

    :param paragraphs: The list of detected filth
    :type paragraphs: int
    :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                   underscore and the two letter upper-case country code, eg "en_GB" or "de_CH"
    :type locale: str
    :param seed: The random seed used to generate the document
    :type seed: int, optional
    :param faker: A Faker object that is used to generate the text
    :type faker: int
    :param filth_types: A list of the ``Filth.type`` to generate
    :type filth_types: List[str]
    :param fake_text_function: A function that will generate a 1-3 sentances of text
    :type fake_text_function: Callable, optional
    :return: The document and a list of `KnownFilthItem`\\ s
    :rtype: Tuple[str, List[KnownFilthItem]]

    """
    pass
