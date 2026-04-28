import warnings
from typing import Optional, Sequence, Generator, Dict, Type, Union, List

from . import detectors
from . import post_processors
from .detectors import Detector
from .post_processors import PostProcessor
from .filth import Filth


class Scrubber:
    """The Scrubber class is used to clean personal information out of dirty
    dirty text. It manages a set of ``Detector``'s that are each responsible
    for identifying ``Filth``. ``PostProcessor`` objects are used to alter
    the found Filth. This could be to replace the Filth with a hash or token.
    """

    def __init__(self, detector_list: Optional[Sequence[Union[Type[Detector], Detector, str]]] = None,
                 post_processor_list: Optional[Sequence[Union[Type[PostProcessor], PostProcessor, str]]] = None,
                 locale: Optional[str] = None):
        """Create a ``Scrubber`` object.

        :param detector_list: The list of detectors to use in this scrubber.
        :type detector_list: Optional[Sequence[Union[Type[Detector], Detector, str]]]
        :param post_processor_list: The locale that the phone number should adhere to.
        :type post_processor_list: Optional[Sequence[Union[Type[Detector], Detector, str]]]
        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str, optional
        """
        super().__init__()

        # instantiate all of the detectors which, by default, uses all of the
        # detectors that are in the detectors.types dictionary
        self._detectors = {}  # type: Dict[str, Detector]
        self._post_processors = []  # type: List[PostProcessor]

        if locale is None:
            locale = 'en_US'
        self._locale = locale  # type: str

        if detector_list is None:
            # First we gather all detectors that should automatically load
            detector_list = [
                detector
                for detector in detectors.catalogue.detector_catalogue.get_all().values()
                if detector.autoload and (
                    # Then we filter out ones that don't support the current locale
                    not hasattr(detector, 'supported_locale') or (
                        hasattr(detector, 'supported_locale') and
                        detector.supported_locale(locale)  # type: ignore
                    )
                )
            ]

        for detector in detector_list:
            self.add_detector(detector, warn=True)

        if post_processor_list is None:
            post_processor_list = [
                post_processor
                for post_processor in sorted(
                    post_processors.catalogue.post_processor_catalogue.get_all().values(),
                    key=lambda pp: pp.index,
                )
                if post_processor.autoload
            ]

        for post_processor in post_processor_list:
            self.add_post_processor(post_processor)

    def add_detector(self, detector: Union[Detector, Type[Detector], str], warn: bool = True):
        """Add a ``Detector`` to Scrubber

        You can add a detector to a ``Scrubber`` by passing one of three objects to this function:

            1. the uninitalised class to this function, which initialises the class with default settings.
            2. an instance of a ``Detector`` class, where you can initialise it with the settings desired.
            3. a string containing the name of the detector, which again initialises the class with default settings.

        .. code:: pycon

            >>> import scrubadub
            >>> scrubber = scrubadub.Scrubber(detector_list=[])
            >>> scrubber.add_detector(scrubadub.detectors.CreditCardDetector)
            >>> scrubber.add_detector('skype')
            >>> detector = scrubadub.detectors.DateOfBirthDetector(require_context=False)
            >>> scrubber.add_detector(detector)

        :param detector: The ``Detector`` to add to this scrubber.
        :type detector: a Detector class, a Detector instance, or a string with the detector's name
        :param warn: raise a warning if the locale is not supported by the detector.
        :type warn: bool, default True
        """
        pass

    def remove_detector(self, detector: Union[Detector, Type[Detector], str]):
        """Remove a ``Detector`` from a Scrubber

        You can remove a detector from a ``Scrubber`` by passing one of three objects to this function:

            1. the uninitalised class to this function, which removes the initalised detector of the same name.
            2. an instance of a ``Detector`` class, which removes the initalised detector of the same name.
            3. a string containing the name of the detector, which removed the detector of that name.

        .. code:: pycon

            >>> import scrubadub
            >>> scrubber = scrubadub.Scrubber()
            >>> scrubber.remove_detector(scrubadub.detectors.CreditCardDetector)
            >>> scrubber.remove_detector('url')
            >>> detector = scrubadub.detectors.email.EmailDetector()
            >>> scrubber.remove_detector(detector)

        :param detector: The ``Detector`` to remove from this scrubber.
        :type detector: a Detector class, a Detector instance, or a string with the detector's name
        """
        pass

    def _check_and_add_detector(self, detector: Detector, warn: bool = False):
        """Check the types and add the detector to the scrubber"""
        pass

    def add_post_processor(self, post_processor: Union[PostProcessor, Type[PostProcessor], str], index: int = None):
        """Add a ``PostProcessor`` to a Scrubber

        You can add a post-processor to a ``Scrubber`` by passing one of three objects to this function:

            1. the uninitalised class to this function, which initialises the class with default settings.
            2. an instance of a ``PostProcessor`` class, where you can initialise it with the settings desired.
            3. a string containing the name of the detector, which again initialises the class with default settings.

        .. code:: pycon

            >>> import scrubadub, scrubadub.post_processors
            >>> scrubber = scrubadub.Scrubber()
            >>> scrubber.add_post_processor('filth_replacer')
            >>> scrubber.add_post_processor(scrubadub.post_processors.PrefixSuffixReplacer)

        :param post_processor: The ``PostProcessor`` to remove from this scrubber.
        :type post_processor: a PostProcessor class, a PostProcessor instance, or a string with the post-processor's
            name
        """
        pass

    def remove_post_processor(self, post_processor: Union[PostProcessor, Type[PostProcessor], str]):
        """Remove a ``PostProcessor`` from a Scrubber

        You can remove a post-processor from a ``Scrubber`` by passing one of three objects to this function:

            1. the uninitalised class to this function, which removes the initalised post-processor of the same name.
            2. an instance of a ``PostProcessor`` class, which removes the initalised post-processor of the same name.
            3. a string containing the name of the detector, which removed the post-processor of that name.

        .. code:: pycon

            >>> import scrubadub, scrubadub.post_processors
            >>> scrubber = scrubadub.Scrubber()
            >>> scrubber.remove_post_processor('filth_type_replacer')
            >>> scrubber.remove_post_processor(scrubadub.post_processors.PrefixSuffixReplacer)

        :param post_processor: The ``PostProcessor`` to remove from this scrubber.
        :type post_processor: a PostProcessor class, a PostProcessor instance, or a string with the post-processor's
            name
        """
        pass

    def _check_and_add_post_processor(self, post_processor: PostProcessor, index: int = None):
        """Check the types and add the PostProcessor to the scrubber"""
        pass

    def clean(self, text: str, **kwargs) -> str:
        """This is the master method that cleans all of the filth out of the
        dirty dirty ``text``. All keyword arguments to this function are passed
        through to the  ``Filth.replace_with`` method to fine-tune how the
        ``Filth`` is cleaned.
        """
        pass

    def clean_documents(self, documents: Union[Sequence[str], Dict[Optional[str], str]], **kwargs) -> \
            Union[Dict[Optional[str], str], Sequence[str]]:
        """This is the master method that cleans all of the filth out of the
        dirty dirty ``text``. All keyword arguments to this function are passed
        through to the  ``Filth.replace_with`` method to fine-tune how the
        ``Filth`` is cleaned.
        """
        pass

    def _replace_text(
            self, text: str, filth_list: Sequence[Filth], document_name: Optional[str], **kwargs
    ) -> str:
        pass

    def _post_process_filth_list(self, filth_list: Sequence[Filth]) -> Sequence[Filth]:
        # We are collating all Filths so that they can all be passed to the post processing step together.
        # This is needed for some operations within the PostProcesssors.
        # It could be improved if we know which post processors need collated Filths.
        pass

    def iter_filth(
            self, text: str, document_name: Optional[str] = None, run_post_processors: bool = True
    ) -> Generator[Filth, None, None]:
        """Iterate over the different types of filth that can exist.
        """
        pass

    @staticmethod
    def _detector_iter_filth_iterator(detector: Detector, document_list: Sequence[str],
                                      document_names: Sequence[Optional[str]]) -> Generator[Filth, None, None]:
        pass

    def iter_filth_documents(
            self,
            documents: Union[Sequence[str], Dict[Optional[str], str]],
            run_post_processors: bool = True
    ) -> Generator[Filth, None, None]:
        """Iterate over the different types of filth that can exist."""
        pass

    @staticmethod
    def _sort_filths(filth_list: Sequence[Filth]) -> List[Filth]:
        """Sorts a list of filths, needed before merging and concatenating"""
        pass

    @staticmethod
    def _merge_filths(filth_list: Sequence[Filth]) -> Generator[Filth, None, None]:
        """This is where the Scrubber does its hard work and merges any
        overlapping filths.
        """
        pass
