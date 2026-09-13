# [M] CVE-2022-40307

## Summary
Severity: Medium
Advisory: CVE-2022-40307
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-09
Source: https://osv.dev/vulnerability/CVE-2022-40307
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.19.8. drivers/firmware/efi/capsule-loader.c has a race condition with a resultant use-after-free.

## References
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://www.debian.org/security/2022/dsa-5257
- https://lists.debian.org/debian-lts-announce/2022/10/msg00000.html
- https://github.com/torvalds/linux/commit/9cb636b5f6a8cc6d1b50809ec8f8d33ae0c84c95
