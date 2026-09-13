# [M] CVE-2018-1096

## Summary
Severity: Medium
Advisory: CVE-2018-1096
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-04-05
Source: https://osv.dev/vulnerability/CVE-2018-1096
Type: osv

## Details
An input sanitization flaw was found in the id field in the dashboard controller of Foreman before 1.16.1. A user could use this flaw to perform an SQL injection attack on the back end database.

## References
- http://projects.theforeman.org/issues/23028
- https://access.redhat.com/errata/RHSA-2018:2927
- https://bugzilla.redhat.com/show_bug.cgi?id=1561061
