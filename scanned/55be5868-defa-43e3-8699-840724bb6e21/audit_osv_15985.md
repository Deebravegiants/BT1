# [M] CVE-2019-20924

## Summary
Severity: Medium
Advisory: CVE-2019-20924
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-23
Source: https://osv.dev/vulnerability/CVE-2019-20924
Type: osv

## Details
A user authorized to perform database queries may trigger denial of service by issuing specially crafted queries which trigger an invariant in the IndexBoundsBuilder. This issue affects MongoDB Server v4.2 versions prior to 4.2.2.

## References
- https://jira.mongodb.org/browse/SERVER-44377
