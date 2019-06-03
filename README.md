# funnel-technical-test

### Intro <br/>
This repo is the submission to Funnel's technical test.

###  Prerequisits <br/>
This is written for for python 3.6. It does not require any additional
packages outside the Python Standard Library

### Running the script <br/>
Running the script via the python interpretor:

`\>\> python web_traffic_report.py <log_file_path> [-from <Date>] [-to <Date>] [-delim <Delimiter>]`

#### Inputs<br/>
`<log_file_path>`        
Path to the log file, requires CSV format, A header is<br>
required and the following columns are required; timestamp,<br/>
listed in ascending order; userid, a user specific id; url,<br/>
which site was visited. The columns does not need to be in<br/>
any specific order any other columns will not affect the script.<br/>
                        
`-from <Date>`       
  Optional: From which date log entries shall be included.<br/>
  Date shall be on the format YYYY-MM-DD HH:mm:ss Default is<br/>
  from beginning of log.<br/>
  
`-to <Date>`       
  - Optional: To which date log entries shall be included.<br/>
  Default is the end of log.<br/>
  
`-delim <Delimiter>`      
  - Optional: If the CSV file has a different delimiter.<br/>
  Default is ','<br/>
  
`-report_name <FileName>` 
  - Optional: Basic report output CSV file name. If omitted<br/>
  report will not be saved.<br/>

### Testing<br/>
The tests are written in the file test.py which can be run by: <br/>

`\>\> python test.py <br/>`

The tests creates a fake log called "fake_log_{i}.csv" where i is is the first number <br/>
for which the file does not exist, if it fails the first 100 times it will give up <br/>
and raise a Runtime Error. <br/>
