from datetime import datetime
import csv
import sys

# Log file settings
DATE_FORMAT = "%Y-%m-%d %H:%M:%SUTC"


def main(test_inputs=None):

    if test_inputs is None:
        inputs = iter(sys.argv)
        _ = next(inputs)  # Discard file name
    else:
        inputs = iter(test_inputs)

    # First argument shall be log path
    log_path = next(inputs, None)

    if log_path is None:
        # If no arguments has been passed print help text
        print("""
            Syntax:
            traffic_report <log_file_path> [-from <Date>] [-to <Date>] [-delim <Delimiter>]

            Inputs
            <log_file_path>         - Path to the log file, requires CSV format
            -from <Date>            - From which date log entries shall be included. Date shall be on the format YYYY-MM-DD HH:mm:ss Default is from beginning of log.
            -to <Date>              - To which date log entries shall be included. Default is the end of log.
            -delim <Delimiter>      - If the CSV file has a different delimiter. Default is ','
            -report_name <FileName> - Basic repot output file name. If omitted report will not be saved.

            """)
        return

    # Set default values
    from_date = None
    to_date = None
    report_file_name = None
    delimiter = ","

    # Iterate over the remaining arguments
    argument = next(inputs, None)
    while argument is not None:
        if argument.lower() == "-from":
            from_date = datetime.strptime(next(inputs), "%Y-%m-%d %H:%M:%S")
        elif argument.lower() == "-to":
            to_date = datetime.strptime(next(inputs), "%Y-%m-%d %H:%M:%S")
        elif argument.lower() == "-delim":
            delimiter = next(inputs)
        elif argument.lower() == "-report_name":
            report_file_name = next(inputs)
        else:
            raise KeyError("Unknown paramter, allowed arguments are: -from, -to, -delim")
        argument = next(inputs, None)

    return GetBasicReport(log_path, from_date, to_date, report_file_name, delimiter)


def LogEntries(log_path, from_date=None, to_date=None, delimiter=","):

    with open(log_path) as f:
        reader = csv.reader(f, delimiter=delimiter)
        header = [tmp.strip() for tmp in next(reader)]  # Remove and clean header

        for row in reader:

            temp_dict = {key: value for key, value in zip(header, row) if key}

            # Clean data
            timestamp = datetime.strptime(temp_dict["timestamp"].strip(), DATE_FORMAT)
            url = temp_dict["url"].strip()
            userid = temp_dict["userid"].strip()

            # Yield data if it within the specified dates
            if from_date is None or timestamp >= from_date:
                if to_date is None or timestamp <= to_date:
                    yield url, userid
                else:
                    break


def GetBasicReport(log_path, from_date=None, to_date=None, report_file_name=None, delimiter=","):
    header = ("url", "page_views", "userids")

    urls_stats = {}
    for url, userid in LogEntries(log_path, from_date, to_date, delimiter):
        if url not in urls_stats:
            urls_stats[url] = {"unique_users": set(),
                               "page_views": 0}

        urls_stats[url]["unique_users"].add(userid)
        urls_stats[url]["page_views"] += 1

    # Generate report
    report = []
    for url, stats in urls_stats.items():
        page_views = stats["page_views"]
        userids = len(stats["unique_users"])
        report.append((url, page_views, userids))

    # If output file name has not been specified return t
    if report_file_name is None:
        print("{:20}{:>15}{:>15}".format(*header))
        for row in report:
            print("{:20}{:15}{:15}".format(*row))
        return report
    else:
        SaveReport(report, report_file_name)


def SaveReport(report, report_file_name):
    if not report_file_name.endswith(".csv") or "." not in report_file_name:
        report_file_name += ".csv"
    with open(report_file_name, 'w', newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["url", "page_views", "userids"])  # Write header
        wr.writerows(report)


if __name__ == '__main__':
    main()
