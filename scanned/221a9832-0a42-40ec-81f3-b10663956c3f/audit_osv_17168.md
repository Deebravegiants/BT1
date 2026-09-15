# [H] CVE-2020-13398

## Summary
Severity: High
Advisory: CVE-2020-13398
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2020-05-22
Source: https://osv.dev/vulnerability/CVE-2020-13398
Type: osv

## Details
An issue was discovered in FreeRDP before 2.1.1. An out-of-bounds (OOB) write vulnerability has been detected in crypto_rsa_common in libfreerdp/crypto/crypto.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00080.html
- https://github.com/FreeRDP/FreeRDP/commit/8fb6336a4072abcee8ce5bd6ae91104628c7bb69
- https://github.com/FreeRDP/FreeRDP/compare/2.1.0...2.1.1
- https://lists.debian.org/debian-lts-announce/2020/08/msg00054.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://usn.ubuntu.com/4379-1/
- https://usn.ubuntu.com/4382-1/
- https://github.com/FreeRDP/FreeRDP/commit/8305349a943c68b1bc8c158f431dc607655aadea
