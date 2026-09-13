# [M] CVE-2018-11503

## Summary
Severity: Medium
Advisory: CVE-2018-11503
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-26
Source: https://osv.dev/vulnerability/CVE-2018-11503
Type: osv

## Details
The isfootnote function in markdown.c in libmarkdown.a in DISCOUNT 2.2.3a allows remote attackers to cause a denial of service (heap-based buffer over-read) via a crafted file, as demonstrated by mkd2html.

## References
- https://lists.debian.org/debian-lts-announce/2018/09/msg00009.html
- https://www.debian.org/security/2018/dsa-4293
- https://github.com/Orc/discount/issues/189#issuecomment-392247798
