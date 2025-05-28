# Mailst: send personalized emails to your students
# Copyright (C) 2014-2020 Jesus Arias Fisteus
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#


def add_cmd_arguments(parser):
    """Add the standard mailst command-line arguments to an argparse parser.

    Returns the same parser object.

    """
    parser.add_argument(
        "--send-emails",
        default=False,
        action="store_true",
        help=(
            "Really send the emails. By default they "
            "are not actually sent, although the messages "
            "are created and a connection to the SMTP "
            "server is established."
        ),
    )
    parser.add_argument(
        "--send-to-recipients",
        default=False,
        action="store_true",
        help=(
            "Really send the emails to the recipients "
            "instead of sending to the From field. "
            "They are sent to the From field if this option"
            "is not set."
        ),
    )
    parser.add_argument(
        "-p",
        "--just-print",
        default=False,
        action="store_true",
        help=(
            "Just print the emails to stdout (does neither "
            "send emails nor connect to the SMTP server.)"
        ),
    )
    parser.add_argument(
        "-m",
        "--max-num-emails",
        type=int,
        default=0,
        help=(
            "Process no more than this number of emails "
            "(0 means no limit and is the default.)"
        ),
    )
    parser.add_argument(
        "-d",
        "--delay",
        type=float,
        default=None,
        help=(
            "Delay in seconds between consecutive emails. "
            "By default, no delay is applied."
        ),
    )
    parser.add_argument(
        "-s",
        "--send-only-to",
        action="append",
        default=[],
        help=(
            "Email address to send the emails to, "
            "from the list of recipients "
            "they would have been sent to if this option were not present. "
            "This option can be used multiple times."
        ),
    )
    parser.add_argument(
        "-e",
        "--exclude",
        action="append",
        default=[],
        help=(
            "Email address to be excluded. " "This option can be used multiple times."
        ),
    )
    return parser
