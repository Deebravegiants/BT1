# [M] CVE-2018-17294

## Summary
Severity: Medium
Advisory: CVE-2018-17294
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-21
Source: https://osv.dev/vulnerability/CVE-2018-17294
Type: osv

## Details
The matchCurrentInput function inside lou_translateString.c of Liblouis prior to 3.7 does not check the input string's length, allowing attackers to cause a denial of service (application crash via out-of-bounds read) by crafting an input file with certain translation dictionaries.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00038.html
- http://www.securityfocus.com/bid/105511
- https://usn.ubuntu.com/3782-1/
- https://github.com/liblouis/liblouis/commit/5e4089659bb49b3095fa541fa6387b4c40d7396e
- https://github.com/liblouis/liblouis/issues/635
