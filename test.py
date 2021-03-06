import unittest
import os
import csv
from datetime import datetime

# Import
from web_traffic_report import BasicWebReport, main


fake_log = [
    ["2013-09-01 09:00:00UTC", "/contact.html", "12345"],
    ["2013-09-01 09:20:00UTC", "/home.html", "12345"],
    ["2013-09-01 09:30:00UTC", "/home.html", "12344123567uhvcfghbklkiuyfcbk"],
    ["2013-09-01 09:33:00UTC", "/home.html", "12346"],
    ["2013-09-01 09:33:10UTC", "/contact.html", "12345"],
    ["2013-09-01 09:48:00UTC", "/contact.html", "12245"],
    ["2013-09-01 10:00:00UTC", "/about.html", "12345"],
    ["2013-09-01 10:30:00UTC", "/about.html", "12a8f"],
    ["2013-09-01 10:50:00UTC", "/contact.html", "123x5"],
    ["2013-09-01 10:55:00UTC", "/contact.html", "12345"],
    ["2013-09-01 11:00:00UTC", "/contact.html", "12345"],
    ["2013-09-02 11:00:00UTC", "/contact.html", "12345"],
    ["2013-09-03 11:00:00UTC", "/contact.html", "12345"],
    ["2013-09-05 11:00:00UTC", "/contact.html", "12345"],
]


class TestBasicReport(unittest.TestCase):

    def __init__(self, *arg):
        super(TestBasicReport, self).__init__(*arg)
        for i in range(100):
            self.fake_log_name = f"fake_log_{i}.csv"
            if not os.path.exists(self.fake_log_name):
                break
        else:
            raise RuntimeError("Could not crate a fake log")

    def setUp(self):
        """
        Create a fake log to do the tests on
        """
        header = ["timestamp", "url", "userid"]
        with open(self.fake_log_name, "w", newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(header)
            csv_writer.writerows(fake_log)

    def tearDown(self):
        """
        Remove the fake log
        """
        os.remove(self.fake_log_name)

    def test_inputs(self):
        """
        Verifies that the correct Exceptions are
        raised if the input if incorrect
        """
        with self.assertRaises(KeyError):
            main(["-from", "2013-09-01 09:00:01"])  # Expects log path to be first
        with self.assertRaises(ValueError):
            main([self.fake_log_name, "-from", "2013-09-01 09:00:xx"])  # Incorrect date format
        with self.assertRaises(KeyError):
            main([self.fake_log_name, "-randomtag"])  # Unknown tag
        with self.assertRaises(StopIteration):
            main([self.fake_log_name, "-from"])  # Missing argument, date has to follow the "-from" tag
        with self.assertRaises(FileNotFoundError):
            main(["non_existing_file.csv"])  # Non existing file

    def test_log_entry_retriever(self):
        """
        Verifies that the correct values are retreived
        by the log reader, LogEntries. Also verifies
        that all row has been retrived
        """
        n_rows = 0
        n_expected_rows = len(fake_log)
        bwr = BasicWebReport(self.fake_log_name)

        for (url_actual, userid_actual), (_, url_expected, userid_expected) in zip(bwr.LogEntries(), fake_log):
            n_rows += 1
            self.assertEqual(url_actual, url_expected)
            self.assertEqual(userid_actual, userid_expected)
        self.assertEqual(n_rows, n_expected_rows)

    def test_log_entry_retriever_between_dates(self):
        """
        Verifies that the correct values are retreived
        by the log reader LogEntries
        """

        n_rows = 0
        fake_log_partition = fake_log[2:6]
        n_expected_rows = len(fake_log_partition)

        bwr = BasicWebReport(self.fake_log_name)
        bwr.from_date = datetime(2013, 9, 1, 9, 30, 00)
        bwr.to_date = datetime(2013, 9, 1, 10, 0, 00)

        for (url_actual, userid_actual), (_, url_expected, userid_expected) in zip(bwr.LogEntries(), fake_log_partition):
            n_rows += 1
            self.assertEqual(url_actual, url_expected)
            self.assertEqual(userid_actual, userid_expected)
        self.assertEqual(n_rows, n_expected_rows)

    def test_basic_report(self):
        """
        Verifies that the number of uniques user and the
        number of webviews. this uses the whole log file.
        """
        bwr = BasicWebReport(self.fake_log_name)
        report = bwr.GetBasicReport()

        for url, web_views, unique_users in report:
            expected_unique_user = len(set([userid_fake_log for _, url_fake_log, userid_fake_log in fake_log if url == url_fake_log]))
            self.assertEqual(unique_users, expected_unique_user)
            expected_web_views = len([1 for _, url_fake_log, _ in fake_log if url == url_fake_log])
            self.assertEqual(web_views, expected_web_views)

    def test_basic_report_between_dates(self):
        """
        Verifies that the number of uniques user and the
        number of webviews between two dates is working
        as intended. This test relies on the that the
        function "LogEntries" is working properly
        """

        bwr_1 = BasicWebReport(self.fake_log_name)
        bwr_1.from_date = datetime(2013, 9, 1, 9, 30, 00)
        bwr_1.to_date = datetime(2013, 9, 1, 10, 0, 00)

        expected_unique_userids = {}
        expected_web_views = {}

        # As log as previous test are passing LogEntries is assumed to be working as intended
        for url, userid in bwr_1.LogEntries():
            if url not in expected_unique_userids and url not in expected_web_views:
                expected_unique_userids[url] = set()
                expected_web_views[url] = 0

            expected_unique_userids[url].add(userid)
            expected_web_views[url] += 1

        expected_unique_user = {url: len(unique_userid_set) for url, unique_userid_set in expected_unique_userids.items()}

        bwr_2 = BasicWebReport(self.fake_log_name)
        bwr_2.from_date = datetime(2013, 9, 1, 9, 30, 00)
        bwr_2.to_date = datetime(2013, 9, 1, 10, 0, 00)

        report = bwr_2.GetBasicReport()
        for url, web_views, unique_users in report:
            self.assertEqual(unique_users, expected_unique_user[url])
            self.assertEqual(web_views, expected_web_views[url])

    def test_main_vs_GetBasicReport(self):
        """
        This verifies that main and GetBasicReport yields
        the same results.
        """

        bwr = BasicWebReport(self.fake_log_name)
        bwr.from_date = datetime(2013, 9, 1, 9, 30, 00)
        bwr.to_date = datetime(2013, 9, 1, 10, 0, 00)

        main_report = main([self.fake_log_name, "-from", str(bwr.from_date), "-to", str(bwr.to_date)])
        get_basic_report = bwr.GetBasicReport()
        self.assertEqual(main_report, get_basic_report)


if __name__ == "__main__":
    unittest.main()
