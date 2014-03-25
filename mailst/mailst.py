import re
import decimal
import smtplib
import email.encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import os.path
import time
import sys


class Column:
    def __init__(self, key, is_email=False, is_file=False):
        self.key = key
        self.is_email=False
        self.is_file = is_file

    def as_dict(self, value):
        return {self.key: value}


class EmailColumn(Column):
    def __init__(self, key):
        super().__init__(key, is_email=True)


class NameColumn(Column):
    def __init__(self, key):
        super().__init__(key)

    def as_dict(self, name):
        d = {self.key: name}
        uncapitalized = NameColumn._uncapitalize(name)
        d[self.key + '_uncapitalized'] = uncapitalized
        return d

    @staticmethod
    def _uncapitalize(name):
        return NameColumn._uncapitalize_spanish(name)

    _lowercase_n_re = re.compile(r'[^\A]Ñ')

    def _uncapitalize_spanish(name):
        """From NAME SURNAME returns Name Surname"""
        names = [n.swapcase().capitalize() for n in name.split(' ')]
        names = [NameColumn._lowercase_n_re.sub('ñ', n) for n in names]
        for i in range(0, len(names)):
            parts = names[i].split('-')
            for j in range(1, len(parts)):
                parts[j] = parts[j].capitalize()
            names[i] = '-'.join(parts)
        return ' '.join(names).strip()


class GradeColumn(Column):
    def __init__(self, key, max_grade=None):
        self.max_grade = max_grade
        super().__init__(key)

    def as_dict(self, grade):
        d = {self.key: GradeColumn.grade(grade)}
        if self.max_grade is not None:
            d[self.key + '_max'] = self.max_grade
        return d

    @staticmethod
    def grade(value):
        if value == '':
            return None
        elif ',' in value:
            return decimal.Decimal(re.sub(',', '.', value))
        else:
            return decimal.Decimal(value)


class FileColumn(Column):
    def __init__(self, key, base_path=None, filename_template=None,
                 content_type=None):
        self.base_path = base_path
        self.filename_template = filename_template
        self.content_type = content_type
        super().__init__(key, self._get_filename, is_file=True)

    def as_dict(self, value):
        return {self.key: AttachmentFile(self._get_filename(value),
                                         self.content_type)}

    def _get_filename(self, value):
        if self.filename_template is None:
            filename = value
        else:
            filename = self.filename_template.format(value)
        if self.base_path is not None:
            filename = os.path.join(self.base_path, filename)
        return filename


class AttachmentFile:
    def __init__(self, filename, content_type):
        self.filename = filename
        self.content_type = content_type
        if self.content_type is not None:
            parts = self.content_type.split('/')
            self.main_type = parts[0]
            self.subtype = parts[1]
        else:
            self.main_type = 'application'
            self.subtype = 'octent-stream'

    def as_mime_part(self):
        part = MIMEBase(self.main_type, self.subtype)
        with open(self.filename, 'rb') as f:
            part.set_payload(f.read())
        part.add_header('Content-Disposition',
                        'attachment; filename="{}"'\
                            .format(os.path.basename(self.filename)))
        email.encoders.encode_base64(part)
        return part


class Recipient:
    def __init__(self, columns=None, values=None):
        self.email = None
        self.file_columns = []
        if columns and values:
            for column, value in zip(columns, values):
                self.set_column(column, value)

    def set_column(self, column, value):
        for key, value in column.as_dict(value).items():
            setattr(self, key, value)
        if column.is_email:
            self.email = value
        if column.is_file:
            self.file_columns.append(column)

    def exclude(self):
        return False

    def pretty_email(self):
        return self.email

    def __str__(self):
        return 'Email address: ' + self.email


class Mailer:
    def __init__(self, smtp_server, subject, template_text, recipients,
                 from_field, cc_field=None):
        self.smtp_server = smtp_server
        self.subject = subject
        self.template_text = template_text
        self.recipients = recipients
        self.from_field = from_field
        self.cc_field = cc_field

    def send(self, simulate=True, print_mails=False, alt_to_field=None,
             max_num_emails=0, delay=None):
        smtp_client = smtplib.SMTP(self.smtp_server)
        num_emails = 0
        for recipient in [r for r in self.recipients if not r.exclude()]:
            message = self._build_message(recipient, alt_to_field)
            if print_mails:
                print(message)
            if not simulate:
                smtp_client.send_message(message)
                if alt_to_field is None:
                    print('Email sent to:', recipient.pretty_email(),
                          file=sys.stderr)
                else:
                    print('Email sent to:', alt_to_field,
                          'instead of', recipient.pretty_email(),
                          file=sys.stderr)
            else:
                if alt_to_field is None:
                    print('Email simulated (not sent) to:',
                          recipient.pretty_email(), file=sys.stderr)
                else:
                    print('Email simulated (not sent) to:', alt_to_field,
                          'instead of', recipient.pretty_email(),
                          file=sys.stderr)
            num_emails += 1
            if max_num_emails and max_num_emails <= num_emails:
                break
            if delay is not None:
                time.sleep(delay)
        smtp_client.quit()

    def test(self, max_num_emails=0):
        num_emails = 0
        for recipient in [r for r in self.recipients if not r.exclude()]:
            print(self._build_test_message(recipient))
            print()
            num_emails += 1
            if max_num_emails and max_num_emails <= num_emails:
                break
        for recipient in [s for s in self.recipients if s.exclude()]:
            print('Excluded: ', recipient)

    def _build_message(self, recipient, alt_to_field):
        text_part = MIMEText(self.template_text.format(recipient))
        if len(recipient.file_columns) == 0:
            message = text_part
        else:
            message = MIMEMultipart()
            message.attach(text_part)
            for column in recipient.file_columns:
                message.attach(getattr(recipient, column.key).as_mime_part())
        message['Subject'] = self.subject
        message['From'] = self.from_field
        if not alt_to_field:
            message['To'] = recipient.pretty_email()
        else:
            message['To'] = alt_to_field
        if self.cc_field:
            message['Cc'] = self.cc_field
        return message

    def _build_test_message(self, recipient):
        message = {}
        message['Recipient'] = str(recipient)
        message['Attachments'] = []
        message['Body_text'] = self.template_text.format(recipient)
        if len(recipient.file_columns) == 0:
            message['Type'] = 'NoMultipartMessage'
        else:
            message['Type'] = 'MultipartMessage'
            for column in recipient.file_columns:
                message['Attachments'].append(getattr(recipient, column.key))
        message['Subject'] = self.subject
        message['From'] = self.from_field
        message['To'] = recipient.pretty_email()
        if self.cc_field:
            message['Cc'] = self.cc_field
        main_text = ('Recipient: {}\n'
                     'Format: {}\n'
                     'From: {}\n'
                     'To: {}\n'
                     'Subject: {}\n\n'
                     '{}\n'
                     ).format(message['Recipient'], message['Type'],
                              message['From'], message['To'],
                              message['Subject'], message['Body_text'])
        attachments = ''.join([('Attachment {0.filename} '
                                '[{0.main_type}/{0.subtype}]'
                               ).format(attachment) \
                               for attachment in message['Attachments']])
        return '\n'.join((main_text, attachments))
