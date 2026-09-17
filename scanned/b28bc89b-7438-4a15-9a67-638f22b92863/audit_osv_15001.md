# [M] CVE-2019-12904

## Summary
Severity: Medium
Advisory: CVE-2019-12904
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-06-20
Source: https://osv.dev/vulnerability/CVE-2019-12904
Type: osv

## Details
In Libgcrypt 1.8.4, the C implementation of AES is vulnerable to a flush-and-reload side-channel attack because physical addresses are available to other processes. (The C implementation is used on platforms where an assembly-language implementation is unavailable.) NOTE: the vendor's position is that the issue report cannot be validated because there is no description of an attack

## References
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00049.html
- https://dev.gnupg.org/T4541
- https://github.com/gpg/libgcrypt/commit/a4c561aab1014c3630bc88faf6f5246fee16b020
- https://github.com/gpg/libgcrypt/commit/daedbbb5541cd8ecda1459d3b843ea4d92788762
