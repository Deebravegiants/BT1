# [M] Moderate severity vulnerability that affects mailman

## Summary
Severity: Medium
Advisory: GHSA-xqvg-xm9m-p2c4
CVE: CVE-2018-13796
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-09-11
Source: https://github.com/advisories/GHSA-xqvg-xm9m-p2c4
Type: github-advisory

## Affected
- PyPI: `mailman` — affected >=0 <2.1.28

## Details
An issue was discovered in GNU Mailman before 2.1.28. A crafted URL can cause arbitrary text to be displayed on a web page from a trusted site.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-13796
- https://bugs.launchpad.net/mailman/+bug/1780874
- https://github.com/advisories/GHSA-xqvg-xm9m-p2c4
- https://lists.debian.org/debian-lts-announce/2018/07/msg00034.html
- https://security.gentoo.org/glsa/201904-10
- https://usn.ubuntu.com/4348-1
- https://www.mail-archive.com/mailman-users@python.org/msg71003.html
