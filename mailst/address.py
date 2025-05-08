import email.utils


class Address:
    def __init__(self, email=None, full_name=None):
        self.email = email
        self.full_name = full_name

    @property
    def name_and_email(self):
        if not self.email:
            raise ValueError("The user has no email")
        return email.utils.formataddr((self.full_name, self.email))
