# [H] CVE-2017-15572

## Summary
Severity: High
Advisory: CVE-2017-15572
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-10-18
Source: https://osv.dev/vulnerability/CVE-2017-15572
Type: osv

## Details
In Redmine before 3.2.6 and 3.3.x before 3.3.3, remote attackers can obtain sensitive information (password reset tokens) by reading a Referer log, because account/lost_password does not use a redirect.

## References
- https://www.debian.org/security/2018/dsa-4191
- https://www.redmine.org/issues/24416
- https://www.redmine.org/projects/redmine/wiki/Security_Advisories
