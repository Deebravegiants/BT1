# [H] An issue was discovered in function `_libssh2_packet_add` in libssh2 1.10.0 allows attackers to...

## Summary
Severity: High
Advisory: JLSEC-2025-189
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-27
Source: https://osv.dev/vulnerability/JLSEC-2025-189
Type: osv

## Affected
- Julia: `LibSSH2_jll` — affected >=1.10.1+0 <1.11.0+0

## Details
An issue was discovered in function `_libssh2_packet_add` in libssh2 1.10.0 allows attackers to access out of bounds memory.

## References
- https://github.com/libssh2/libssh2/pull/476
- https://lists.debian.org/debian-lts-announce/2023/09/msg00006.html
- https://security.netapp.com/advisory/ntap-20231006-0002/
