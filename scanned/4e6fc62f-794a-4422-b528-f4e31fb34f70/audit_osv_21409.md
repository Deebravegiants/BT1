# [M] CVE-2021-42781

## Summary
Severity: Medium
Advisory: CVE-2021-42781
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-04-18
Source: https://osv.dev/vulnerability/CVE-2021-42781
Type: osv

## Details
Heap buffer overflow issues were found in Opensc before version 0.22.0 in pkcs15-oberthur.c that could potentially crash programs using the library.

## References
- https://lists.debian.org/debian-lts-announce/2023/06/msg00025.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00026.html
- https://security.gentoo.org/glsa/202209-03
- https://bugzilla.redhat.com/show_bug.cgi?id=2016439
- https://github.com/OpenSC/OpenSC/commit/05648b06
- https://github.com/OpenSC/OpenSC/commit/17d8980c
- https://github.com/OpenSC/OpenSC/commit/40c50a3a
- https://github.com/OpenSC/OpenSC/commit/5d4daf6c
- https://github.com/OpenSC/OpenSC/commit/cae5c71f
