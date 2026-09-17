# [H] CVE-2019-8383

## Summary
Severity: High
Advisory: CVE-2019-8383
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-17
Source: https://osv.dev/vulnerability/CVE-2019-8383
Type: osv

## Details
An issue was discovered in AdvanceCOMP through 2.1. An invalid memory address occurs in the function adv_png_unfilter_8 in lib/png.c. It can be triggered by sending a crafted file to a binary. It allows an attacker to cause a Denial of Service (Segmentation fault) or possibly have unspecified other impact when a victim opens a specially crafted file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J23C6QSTJMQ467KAI6QG54AE4MZRLPQV/
- https://access.redhat.com/errata/RHSA-2019:2332
- https://lists.debian.org/debian-lts-announce/2021/12/msg00034.html
- https://research.loginsoft.com/bugs/invalid-memory-access-in-adv_png_unfilter_8-advancecomp/
- https://sourceforge.net/p/advancemame/bugs/272/
