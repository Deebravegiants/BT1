# [H] CVE-2021-42381

## Summary
Severity: High
Advisory: CVE-2021-42381
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-15
Source: https://osv.dev/vulnerability/CVE-2021-42381
Type: osv

## Details
A use-after-free in Busybox's awk applet leads to denial of service and possibly code execution when processing a crafted awk pattern in the hash_init function

## References
- https://claroty.com/team82/research/unboxing-busybox-14-vulnerabilities-uncovered-by-claroty-jfrog
- https://lists.debian.org/debian-lts-announce/2025/01/msg00012.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6T2TURBYYJGBMQTTN2DSOAIQGP7WCPGV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UQXGOGWBIYWOIVXJVRKHZR34UMEHQBXS/
- https://jfrog.com/blog/unboxing-busybox-14-new-vulnerabilities-uncovered-by-claroty-and-jfrog/
- https://security.netapp.com/advisory/ntap-20211223-0002/
