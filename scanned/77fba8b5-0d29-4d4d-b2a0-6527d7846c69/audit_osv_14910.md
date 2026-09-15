# [M] CVE-2019-12417

## Summary
Severity: Medium
Advisory: CVE-2019-12417
Aliases: GHSA-q3p4-gw7r-wqjc, PYSEC-2019-216, PYSEC-2026-617
CVSS: 4.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-10-30
Source: https://osv.dev/vulnerability/CVE-2019-12417
Type: osv

## Details
A malicious admin user could edit the state of objects in the Airflow metadata database to execute arbitrary javascript on certain page views. This also presented a Local File Disclosure vulnerability to any file readable by the webserver process.

## References
- https://lists.apache.org/thread.html/f3aa5ff9c7cdb5424b6463c9013f6cf5db83d26c66ea77130cbbe1bc%40%3Cusers.airflow.apache.org%3E
