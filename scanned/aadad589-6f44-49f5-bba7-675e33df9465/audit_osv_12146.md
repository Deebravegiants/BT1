# [H] CVE-2018-1056

## Summary
Severity: High
Advisory: CVE-2018-1056
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2018-1056
Type: osv

## Details
An out-of-bounds heap buffer read flaw was found in the way advancecomp before 2.1-2018/02 handled processing of ZIP files. An attacker could potentially use this flaw to crash the advzip utility by tricking it into processing crafted ZIP files.

## References
- https://lists.debian.org/debian-lts-announce/2018/02/msg00016.html
- https://lists.debian.org/debian-lts-announce/2019/03/msg00004.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00034.html
- https://usn.ubuntu.com/3570-1/
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=889270
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1056
- https://sourceforge.net/p/advancemame/bugs/259/
