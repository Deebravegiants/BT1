# [H] Cross Site Request Forgery in mailman

## Summary
Severity: High
Advisory: GHSA-xq58-69h2-765m
CVE: CVE-2021-44227
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-16
Source: https://github.com/advisories/GHSA-xq58-69h2-765m
Type: github-advisory

## Affected
- PyPI: `mailman` — affected >=0 <2.1.38

## Details
In GNU Mailman before 2.1.38, a list member or moderator can get a CSRF token and craft an admin request (using that token) to set a new admin password or make other changes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44227
- https://bugs.launchpad.net/mailman/+bug/1952384
- https://gitlab.com/mailman/mailman
- https://lists.debian.org/debian-lts-announce/2022/06/msg00011.html
