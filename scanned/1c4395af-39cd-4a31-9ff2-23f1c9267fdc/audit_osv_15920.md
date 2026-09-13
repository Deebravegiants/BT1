# [H] CVE-2019-20529

## Summary
Severity: High
Advisory: CVE-2019-20529
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-03-18
Source: https://osv.dev/vulnerability/CVE-2019-20529
Type: osv

## Details
In core/doctype/prepared_report/prepared_report.py in Frappe 11 and 12, data files generated with Prepared Report were being stored as public files (no authentication is required to access; having a link is sufficient) instead of private files.

## References
- https://github.com/frappe/frappe/pull/8884
- https://github.com/frappe/frappe/pull/8885
