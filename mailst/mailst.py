import re
import decimal
import smtplib
from email.mime.text import MIMEText

class Column:
    FIRST_NAME = 'first_name'
    SHORT_NAME = 'short_name'
    EMAIL = 'email'

    def __init__(self, key, adapter_func, max_grade=None):
        self.key = key
        self.adapter_func = adapter_func
        self.max_grade = max_grade

    def adapt(self, value):
        return self.adapter_func(value)

    @staticmethod
    def text(value):
        return value

    @staticmethod
    def name(value):
        return _uncapitalize(value)

    @staticmethod
    def grade(value):
        return decimal.Decimal(re.sub(',', '.', value))


class Student:
    def __init__(self, columns=None, values=None):
        if columns and values:
            for column, value in zip(columns, values):
                self.set_column(column, value)

    def set_column(self, column, value):
        setattr(self, column.key, column.adapt(value))
        if column.key == Column.FIRST_NAME:
            short_name = getattr(self, Column.FIRST_NAME).split(' ')[0]
            setattr(self, Column.SHORT_NAME, short_name)
        if column.max_grade is not None:
            setattr(self, column.key + '_max', column.max_grade)


def send(subject, template_text, students, from_field, cc_field=None,
               simulate=False, print_mails=False, alt_to_field=None,
               max_num_emails=0):
    s = smtplib.SMTP('smtp.uc3m.es')
    num_emails = 0
    for student in students:
        msg = MIMEText(template_text.format(student))
        if not alt_to_field:
            msg['To'] = getattr(student, Column.EMAIL)
        else:
            msg['To'] = alt_to_field
        msg['Subject'] = subject
        msg['From'] = from_field
        if cc_field:
            msg['Cc'] = cc_field
        if print_mails:
            print(msg)
        if not simulate:
            s.send_message(msg)
        num_emails += 1
        if max_num_emails and max_num_emails <= num_emails:
            break
    s.quit()

_lowercase_n_re = re.compile(r'(?<!\ )Ñ')

def _uncapitalize_spanish(name):
    """From NAME SURNAME returns Name Surname"""
    names = [n.swapcase().capitalize() for n in name.split(' ')]
    names = [_lowercase_n_re.sub('ñ', n) for n in names]
    for i in range(0, len(names)):
        parts = names[i].split('-')
        for j in range(1, len(parts)):
            parts[j] = parts[j].capitalize()
        names[i] = '-'.join(parts)
    return ' '.join(names).strip()

_uncapitalize = _uncapitalize_spanish
