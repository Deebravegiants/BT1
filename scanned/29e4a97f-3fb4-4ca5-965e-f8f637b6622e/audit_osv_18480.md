# [H] CVE-2020-27844

## Summary
Severity: High
Advisory: CVE-2020-27844
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-01-05
Source: https://osv.dev/vulnerability/CVE-2020-27844
Type: osv

## Details
A flaw was found in openjpeg's src/lib/openjp2/t2.c in versions prior to 2.4.0. This flaw allows an attacker to provide crafted input to openjpeg during conversion and encoding, causing an out-of-bounds write. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://lists.debian.org/debian-lts-announce/2021/02/msg00011.html
- https://security.gentoo.org/glsa/202101-29
- https://bugzilla.redhat.com/show_bug.cgi?id=1907521
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
