# [H] ALPINE-CVE-2019-17498

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-17498
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2019-10-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-17498
Type: osv

## Affected
- Alpine:v3.10: `libssh2` — affected >=0 <1.9.0-r1
- Alpine:v3.11: `libssh2` — affected >=0 <1.9.0-r1
- Alpine:v3.12: `libssh2` — affected >=0 <1.9.0-r1
- Alpine:v3.13: `libssh2` — affected >=0 <1.9.0-r1
- Alpine:v3.14: `libssh2` — affected >=0 <1.9.0-r1
- Alpine:v3.15: `libssh2` — affected >=0 <1.9.0-r1
- Alpine:v3.16: `libssh2` — affected >=0 <1.9.0-r1
- Alpine:v3.17: `libssh2` — affected >=0 <1.9.0-r1
- Alpine:v3.18: `libssh2` — affected >=0 <1.9.0-r1
- Alpine:v3.19: `libssh2` — affected >=0 <1.9.0-r1
- Alpine:v3.20: `libssh2` — affected >=0 <1.9.0-r1
- Alpine:v3.21: `libssh2` — affected >=0 <1.9.0-r1
- Alpine:v3.22: `libssh2` — affected >=0 <1.9.0-r1
- Alpine:v3.23: `libssh2` — affected >=0 <1.9.0-r1
- Alpine:v3.24: `libssh2` — affected >=0 <1.9.0-r1
- Alpine:v3.9: `libssh2` — affected >=0 <1.9.0-r1

## Details
In libssh2 v1.9.0 and earlier versions, the SSH_MSG_DISCONNECT logic in packet.c has an integer overflow in a bounds check, enabling an attacker to specify an arbitrary (out-of-bounds) offset for a subsequent memory read. A crafted SSH server may be able to disclose sensitive information or cause a denial of service condition on the client system when a user connects to the server.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-17498
