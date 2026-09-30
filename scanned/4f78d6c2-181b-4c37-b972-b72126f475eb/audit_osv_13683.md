# [M] CVE-2018-20805

## Summary
Severity: Medium
Advisory: CVE-2018-20805
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-23
Source: https://osv.dev/vulnerability/CVE-2018-20805
Type: osv

## Details
A user authorized to perform database queries may trigger denial of service by issuing specially crafted queries, which perform an $elemMatch . This issue affects MongoDB Server v4.0 versions prior to 4.0.5 and MongoDB Server v3.6 versions prior to 3.6.10.

## References
- https://jira.mongodb.org/browse/SERVER-38164
