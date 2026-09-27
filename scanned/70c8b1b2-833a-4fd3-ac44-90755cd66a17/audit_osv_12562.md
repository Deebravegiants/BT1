# [H] CVE-2018-1292

## Summary
Severity: High
Advisory: CVE-2018-1292
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-04-20
Source: https://osv.dev/vulnerability/CVE-2018-1292
Type: osv

## Details
Within the 'getReportType' method in Apache Fineract 1.0.0, 0.6.0-incubating, 0.5.0-incubating, 0.4.0-incubating, a hacker could inject SQL to read/update data for which he doesn't have authorization for by way of the 'reportName' parameter.

## References
- https://lists.apache.org/thread.html/a24610817845d022d5fe89cfe21563ef83bea35ca95de867cd2c4ee9%40%3Cdev.fineract.apache.org%3E
- http://www.securityfocus.com/bid/104007
