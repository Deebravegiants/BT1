# [H] ALPINE-CVE-2026-22184

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-22184
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-22184
Type: osv

## Affected
- Alpine:v3.20: `zlib` — affected >=0 <1.3.2-r0
- Alpine:v3.21: `zlib` — affected >=0 <1.3.2-r0
- Alpine:v3.22: `zlib` — affected >=0 <1.3.2-r0
- Alpine:v3.23: `zlib` — affected >=0 <1.3.2-r0
- Alpine:v3.24: `zlib` — affected >=0 <1.3.2-r0

## Details
zlib versions up to and including 1.3.1.2 include a global buffer overflow in the untgz utility located under contrib/untgz. The vulnerability is limited to the standalone demonstration utility and does not affect the core zlib compression library. The flaw occurs when a user executes the untgz command with an excessively long archive name supplied via the command line, leading to an out-of-bounds write in a fixed-size global buffer.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-22184
