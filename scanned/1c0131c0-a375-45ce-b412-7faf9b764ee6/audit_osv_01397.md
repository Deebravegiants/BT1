# [H] ALPINE-CVE-2019-13115

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-13115
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2019-07-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-13115
Type: osv

## Affected
- Alpine:v3.10: `libssh2` — affected >=0 <1.9.0-r0
- Alpine:v3.11: `libssh2` — affected >=0 <1.9.0-r0
- Alpine:v3.12: `libssh2` — affected >=0 <1.9.0-r0
- Alpine:v3.13: `libssh2` — affected >=0 <1.9.0-r0
- Alpine:v3.14: `libssh2` — affected >=0 <1.9.0-r0
- Alpine:v3.15: `libssh2` — affected >=0 <1.9.0-r0
- Alpine:v3.16: `libssh2` — affected >=0 <1.9.0-r0
- Alpine:v3.17: `libssh2` — affected >=0 <1.9.0-r0
- Alpine:v3.18: `libssh2` — affected >=0 <1.9.0-r0
- Alpine:v3.19: `libssh2` — affected >=0 <1.9.0-r0
- Alpine:v3.20: `libssh2` — affected >=0 <1.9.0-r0
- Alpine:v3.21: `libssh2` — affected >=0 <1.9.0-r0
- Alpine:v3.22: `libssh2` — affected >=0 <1.9.0-r0
- Alpine:v3.23: `libssh2` — affected >=0 <1.9.0-r0
- Alpine:v3.24: `libssh2` — affected >=0 <1.9.0-r0
- Alpine:v3.9: `libssh2` — affected >=0 <1.9.0-r0

## Details
In libssh2 before 1.9.0, kex_method_diffie_hellman_group_exchange_sha256_key_exchange in kex.c has an integer overflow that could lead to an out-of-bounds read in the way packets are read from the server. A remote attacker who compromises a SSH server may be able to disclose sensitive information or cause a denial of service condition on the client system when a user connects to the server. This is related to an _libssh2_check_length mistake, and is different from the various issues fixed in 1.8.1, such as CVE-2019-3855.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-13115
