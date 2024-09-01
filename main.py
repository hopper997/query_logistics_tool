import os

from common.util import get_csv_file
from scripts.track_and_parse import write_logistic_detail_to_csv, get_remain_quota


def main():
    csv_file_path = os.path.join("data", get_csv_file()[0])
    csv_file_path = os.path.normpath(csv_file_path).replace('\\', '/')
    write_logistic_detail_to_csv(csv_file_path)
    get_remain_quota()


if __name__ == '__main__':
    main()
