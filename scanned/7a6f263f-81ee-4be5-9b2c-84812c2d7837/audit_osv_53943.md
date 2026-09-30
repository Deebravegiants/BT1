# [C] CVE-2023-33476

## Summary
Severity: Critical
Advisory: CVE-2023-33476
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-33476
Type: osv

## Details
ReadyMedia (MiniDLNA) versions from 1.1.15 up to 1.3.2 is vulnerable to Buffer Overflow. The vulnerability is caused by incorrect validation logic when handling HTTP requests using chunked transport encoding. This results in other code later using attacker-controlled chunk values that exceed the length of the allocated buffer, resulting in out-of-bounds read/write.

## References
- https://sourceforge.net/projects/minidlna/
- https://lists.debian.org/debian-lts-announce/2023/06/msg00027.html
- https://www.debian.org/security/2023/dsa-5434
- https://security.gentoo.org/glsa/202311-12
- https://sourceforge.net/p/minidlna/git/ci/9bd58553fae5aef3e6dd22f51642d2c851225aec/
- https://blog.coffinsec.com/0day/2023/05/31/minidlna-heap-overflow-rca.html
