# [H] ALPINE-CVE-2026-55200

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-55200
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-55200
Type: osv

## Affected
- Alpine:v3.21: `libssh2` — affected >=0 <1.11.1-r2
- Alpine:v3.22: `libssh2` — affected >=0 <1.11.1-r2
- Alpine:v3.23: `libssh2` — affected >=0 <1.11.1-r3
- Alpine:v3.24: `libssh2` — affected >=0 <1.11.1-r3
- Alpine:v3.24: `rust` — affected >=0 <1.96.1-r0

## Details
libssh2 through 1.11.1, fixed in commit 7acf3df contains an out-of-bounds write vulnerability in ssh2_transport_read() that fails to enforce upper bounds on packet_length field. Remote attackers can send crafted SSH packets with excessively large packet_length values to corrupt heap memory and achieve remote code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-55200
