# [M] CVE-2019-2392

## Summary
Severity: Medium
Advisory: CVE-2019-2392
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-23
Source: https://osv.dev/vulnerability/CVE-2019-2392
Type: osv

## Details
A user authorized to perform database queries may trigger denial of service by issuing specially crafted queries, which use the $mod operator to overflow negative values. This issue affects: MongoDB Inc. MongoDB Server v4.4 versions prior to 4.4.1; v4.2 versions prior to 4.2.9; v4.0 versions prior to 4.0.20; v3.6 versions prior to 3.6.20.

## References
- https://jira.mongodb.org/browse/SERVER-43699
