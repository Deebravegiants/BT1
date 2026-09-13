# [H] ALPINE-CVE-2025-26519

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-26519
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-26519
Type: osv

## Affected
- Alpine:v3.16: `musl` — affected >=0.9.13 <1.2.3-r4
- Alpine:v3.17: `musl` — affected >=0.9.13 <1.2.3-r6
- Alpine:v3.18: `musl` — affected >=0.9.13 <1.2.4-r3
- Alpine:v3.19: `musl` — affected >=0.9.13 <1.2.4_git20230717-r5
- Alpine:v3.20: `musl` — affected >=0.9.13 <1.2.5-r1
- Alpine:v3.21: `musl` — affected >=0.9.13 <1.2.5-r9
- Alpine:v3.22: `musl` — affected >=0.9.13 <1.2.5-r10
- Alpine:v3.23: `musl` — affected >=0.9.13 <1.2.5-r10
- Alpine:v3.24: `musl` — affected >=0.9.13 <1.2.5-r10

## Details
musl libc 0.9.13 through 1.2.5 before 1.2.6 has an out-of-bounds write vulnerability when an attacker can trigger iconv conversion of untrusted EUC-KR text to UTF-8.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-26519
