# [M] CVE-2019-20923

## Summary
Severity: Medium
Advisory: CVE-2019-20923
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-23
Source: https://osv.dev/vulnerability/CVE-2019-20923
Type: osv

## Details
A user authorized to perform database queries may trigger denial of service by issuing specially crafted queries, which throw unhandled Javascript exceptions containing types intended to be scoped to the Javascript engine's internals. This issue affects MongoDB Server v4.0 versions prior to 4.0.7.

## References
- https://jira.mongodb.org/browse/SERVER-39481
