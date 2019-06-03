from datetime import datetime
import csv
import sys

# Log file settings


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
            -quiet                  - If the script should print anything
            """)
        return

    bwr = BasicWebReport(log_path=log_path)

    # Iterate over the remaining arguments
    argument = next(inputs, None)
    while argument is not None:
        if argument.lower() == "-from":
            bwr.from_date = datetime.strptime(next(inputs), "%Y-%m-%d %H:%M:%S")
        elif argument.lower() == "-to":
            bwr.to_date = datetime.strptime(next(inputs), "%Y-%m-%d %H:%M:%S")
        elif argument.lower() == "-delim":
            bwr.delimiter = next(inputs)
        elif argument.lower() == "-report_name":
            bwr.report_file_name = next(inputs)
        elif argument.lower() == "-quiet":
            bwr.verbose = False
        else:
            raise KeyError("Unknown paramter, allowed arguments are: -from, -to, -delim")
        argument = next(inputs, None)

    return bwr.GetBasicReport()


class BasicWebReport(object):

    def __init__(self, log_path, from_date=None, to_date=None, report_file_name=None, delimiter=",", verbose=True):
        self.log_path = log_path
        self.from_date = from_date
        self.to_date = to_date
        self.delimiter = delimiter
        self.verbose = verbose
        if report_file_name is not None and not report_file_name.endswith(".csv") and "." not in report_file_name:
            self.report_file_name = report_file_name + ".csv"
        else:
            self.report_file_name = report_file_name

        # Constants
        self.DATE_FORMAT = "%Y-%m-%d %H:%M:%SUTC"

    def LogEntries(self):
        print(self.log_path)
        with open(self.log_path) as f:
            reader = csv.reader(f, delimiter=self.delimiter)
            header = [tmp.strip() for tmp in next(reader)]  # Remove and clean header

            for row in reader:

                temp_dict = {key: value for key, value in zip(header, row) if key}

                # Clean data
                timestamp = datetime.strptime(temp_dict["timestamp"].strip(), self.DATE_FORMAT)
                url = temp_dict["url"].strip()
                userid = temp_dict["userid"].strip()

                # Yield data if it within the specified dates
                if self.from_date is None or timestamp >= self.from_date:
                    if self.to_date is None or timestamp <= self.to_date:
                        yield url, userid
                    else:
                        break

    def GetBasicReport(self):
        """
        Loop through the logs entries that are within
        the specified dates
        """
        urls_stats = {}
        for url, userid in self.LogEntries():
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

        self.OutputReport(report)
        return report

    def OutputReport(self, report):
        """Save and/or print the report"""
        if self.verbose:
            header = ("url", "page_views", "userids")
            print("{:20}{:>15}{:>15}".format(*header))
            for row in report:
                print("{:20}{:15}{:15}".format(*row))

        if self.report_file_name:
            with open(self.report_file_name, 'w', newline="") as f:
                wr = csv.writer(f)
                wr.writerow(["url", "page_views", "userids"])  # Write header
                wr.writerows(report)


if __name__ == '__main__':
    main()
