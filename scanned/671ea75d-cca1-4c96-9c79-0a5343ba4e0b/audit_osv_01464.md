# [M] ALPINE-CVE-2019-1549

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-1549
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-09-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-1549
Type: osv

## Affected
- Alpine:v3.10: `openssl` — affected >=1.1.1 <1.1.1d-r0
- Alpine:v3.11: `openssl` — affected >=1.1.1 <1.1.1d-r1
- Alpine:v3.12: `openssl` — affected >=1.1.1 <1.1.1d-r1
- Alpine:v3.13: `openssl` — affected >=1.1.1 <1.1.1d-r1
- Alpine:v3.14: `openssl` — affected >=1.1.1 <1.1.1d-r1
- Alpine:v3.15: `openssl` — affected >=1.1.1 <1.1.1d-r1
- Alpine:v3.16: `openssl` — affected >=1.1.1 <1.1.1d-r1
- Alpine:v3.17: `openssl` — affected >=1.1.1 <1.1.1d-r1
- Alpine:v3.18: `openssl` — affected >=1.1.1 <1.1.1d-r1
- Alpine:v3.19: `openssl` — affected >=1.1.1 <1.1.1d-r1
- Alpine:v3.20: `openssl` — affected >=1.1.1 <1.1.1d-r1
- Alpine:v3.21: `openssl` — affected >=1.1.1 <1.1.1d-r1
- Alpine:v3.22: `openssl` — affected >=1.1.1 <1.1.1d-r1
- Alpine:v3.23: `openssl` — affected >=1.1.1 <1.1.1d-r1
- Alpine:v3.24: `openssl` — affected >=1.1.1 <1.1.1d-r1
- Alpine:v3.9: `openssl` — affected >=1.1.1 <1.1.1d-r0
- Alpine:v3.15: `openssl3` — affected >=0 <1.1.1d-r1
- Alpine:v3.16: `openssl3` — affected >=0 <1.1.1d-r1

## Details
OpenSSL 1.1.1 introduced a rewritten random number generator (RNG). This was intended to include protection in the event of a fork() system call in order to ensure that the parent and child processes did not share the same RNG state. However this protection was not being used in the default case. A partial mitigation for this issue is that the output from a high precision timer is mixed into the RNG state so the likelihood of a parent and child process sharing state is significantly reduced. If an application already calls OPENSSL_init_crypto() explicitly using OPENSSL_INIT_ATFORK then this problem does not occur at all. Fixed in OpenSSL 1.1.1d (Affected 1.1.1-1.1.1c).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-1549
