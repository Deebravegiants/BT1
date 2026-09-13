# [M] CVE-2018-20803

## Summary
Severity: Medium
Advisory: CVE-2018-20803
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-23
Source: https://osv.dev/vulnerability/CVE-2018-20803
Type: osv

## Details
A user authorized to perform database queries may trigger denial of service by issuing specially crafted queries, which loop indefinitely in mathematics processing while retaining locks. This issue affects MongoDB Server v4.0 versions prior to 4.0.5; MongoDB Server v3.6 versions prior to 3.6.10 and MongoDB Server v3.4 versions prior to 3.4.19.

## References
- https://jira.mongodb.org/browse/SERVER-38070
