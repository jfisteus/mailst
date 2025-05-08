import datetime
import pathlib

from . import address

LOG_FILENAME = ".mailst-sentlog.csv"


class SentLog:
    sent_to: dict[str, datetime.datetime]

    def __init__(self):
        self.sent_to = {}
        self._load_from_file()

    def __contains__(self, address: address.Address) -> bool:
        return address.email in self.sent_to

    def add(self, address: address.Address, timestamp: datetime.datetime) -> None:
        self.sent_to[address.email] = timestamp
        self._append_to_file(address, timestamp)

    def _load_from_file(self) -> None:
        path = pathlib.Path(LOG_FILENAME)
        if path.exists():
            with open(LOG_FILENAME, "r") as f:
                for line in f:
                    email, timestamp = line.strip().split(",")
                    self.sent_to[email] = datetime.datetime.fromisoformat(timestamp)
            print(f"Loaded {len(self.sent_to)} sent email records from the log file.")
        else:
            print("No log file found. Starting with an empty log.")

    def _append_to_file(
        self, address: address.Address, timestamp: datetime.datetime
    ) -> None:
        with open(LOG_FILENAME, "a") as f:
            f.write(f"{address.email},{timestamp.isoformat()}\n")


log = SentLog()
