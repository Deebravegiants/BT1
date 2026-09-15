# [H] CVE-2019-12360

## Summary
Severity: High
Advisory: CVE-2019-12360
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2019-05-27
Source: https://osv.dev/vulnerability/CVE-2019-12360
Type: osv

## Details
A stack-based buffer over-read exists in FoFiTrueType::dumpString in fofi/FoFiTrueType.cc in Xpdf 4.01.01. It can, for example, be triggered by sending crafted TrueType data in a PDF document to the pdftops tool. It might allow an attacker to cause Denial of Service or leak memory data into dump content.

## References
- https://lists.debian.org/debian-lts-announce/2019/06/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EJ3GYFINXANXTQEDN5SON47IJA5277RU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IQBAHQQF2P7E6PL5STST3TGH7VPVXKKQ/
- https://forum.xpdfreader.com/viewtopic.php?f=3&t=41801
