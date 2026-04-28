from .base import Filth
from .. import exceptions


class CredentialFilth(Filth):
    type = 'credential'

    # specify how the username/password are replaced
    username_placeholder = 'USERNAME'
    password_placeholder = 'PASSWORD'

    @property
    def placeholder(self):
        pass

    # override the replace_with method for credentials because the
    # prefix/suffix components are mixed into the placeholder
    def replace_with(self, replace_with='placeholder', **kwargs):
        pass
