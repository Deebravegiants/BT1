# [M] CVE-2021-42374

## Summary
Severity: Medium
Advisory: CVE-2021-42374
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2021-11-15
Source: https://osv.dev/vulnerability/CVE-2021-42374
Type: osv

## Details
An out-of-bounds heap read in Busybox's unlzma applet leads to information leak and denial of service when crafted LZMA-compressed input is decompressed. This can be triggered by any applet/format that

## References
- https://claroty.com/team82/research/unboxing-busybox-14-vulnerabilities-uncovered-by-claroty-jfrog
- https://lists.debian.org/debian-lts-announce/2025/01/msg00012.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6T2TURBYYJGBMQTTN2DSOAIQGP7WCPGV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UQXGOGWBIYWOIVXJVRKHZR34UMEHQBXS/
- https://security.netapp.com/advisory/ntap-20211223-0002/
- https://jfrog.com/blog/unboxing-busybox-14-new-vulnerabilities-uncovered-by-claroty-and-jfrog/
