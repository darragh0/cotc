import sys
from logging import Logger, getLogger
from os import system
from time import sleep
from typing import TYPE_CHECKING

from requests.status_codes import codes as status_codes

from metrics import MetricSnapshot, local_snapshot, remote_snapshot
from sdk import SnapshotPublisher

if TYPE_CHECKING:
    from requests import Response


class App:
    sleep_secs: int
    publisher: SnapshotPublisher
    logger: Logger

    def __init__(self, sleep_secs: int) -> None:
        self.sleep_secs = sleep_secs
        self.publisher = SnapshotPublisher()
        self.logger = getLogger(__name__)

    def run(self) -> int:
        try:
            metric_n: int = 0
            while True:
                metric_n += 1
                self.logger.info("[%d] Sending metrics", metric_n)

                remote: MetricSnapshot = remote_snapshot()
                local: MetricSnapshot = local_snapshot()

                response: Response = self.publisher.send_snapshots(local, remote)

                match response.status_code:
                    case status_codes.OK:
                        self.logger.info("[%d] Metrics sent successfully\n", metric_n)
                    case _:
                        self.logger.info(
                            "[%d] Failed to send metrics: %d\n",
                            metric_n,
                            response.status_code,
                        )

                sleep(self.sleep_secs)
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
            return 1


def main() -> int:
    return App(sleep_secs=1000).run()


if __name__ == "__main__":
    system("/usr/bin/clear")  # noqa: S605
    sys.exit(main())
