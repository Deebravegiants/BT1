# [M] CVE-2020-7926

## Summary
Severity: Medium
Advisory: CVE-2020-7926
Aliases: BIT-mongodb-2020-7926
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-23
Source: https://osv.dev/vulnerability/CVE-2020-7926
Type: osv

## Details
A user authorized to perform database queries may cause denial of service by issuing a specially crafted query which violates an invariant in the server selection subsystem. This issue affects MongoDB Server v4.4 versions prior to 4.4.1. Versions before 4.4 are not affected.

## References
- https://jira.mongodb.org/browse/SERVER-50170
