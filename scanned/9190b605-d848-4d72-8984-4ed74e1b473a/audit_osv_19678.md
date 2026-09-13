# [C] CVE-2021-23654

## Summary
Severity: Critical
Advisory: CVE-2021-23654
Aliases: GHSA-fwf6-rw69-hhj4, PYSEC-2021-866, SNYK-PYTHON-HTMLTOCSV-1582784
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-26
Source: https://osv.dev/vulnerability/CVE-2021-23654
Type: osv

## Details
This affects all versions of package html-to-csv. When there is a formula embedded in a HTML page, it gets accepted without any validation and the same would be pushed while converting it into a CSV file. Through this a malicious actor can embed or generate a malicious link or execute commands via CSV files.

## References
- https://github.com/hanwentao/html2csv/blob/master/html2csv/converter.py
- https://snyk.io/vuln/SNYK-PYTHON-HTMLTOCSV-1582784
