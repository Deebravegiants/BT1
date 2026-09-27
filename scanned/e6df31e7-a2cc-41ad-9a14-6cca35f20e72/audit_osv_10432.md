# [H] CVE-2017-15575

## Summary
Severity: High
Advisory: CVE-2017-15575
CVSS: 7.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2017-10-18
Source: https://osv.dev/vulnerability/CVE-2017-15575
Type: osv

## Details
In Redmine before 3.2.6 and 3.3.x before 3.3.3, Redmine.pm lacks a check for whether the Repository module is enabled in a project's settings, which might allow remote attackers to obtain sensitive differences information or possibly have unspecified other impact.

## References
- https://www.debian.org/security/2018/dsa-4191
- https://www.redmine.org/issues/24307
- https://www.redmine.org/projects/redmine/wiki/Security_Advisories
