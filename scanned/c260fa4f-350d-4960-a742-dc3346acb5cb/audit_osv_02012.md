# [H] ALPINE-CVE-2020-8252

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-8252
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8252
Type: osv

## Affected
- Alpine:v3.12: `libuv` — affected >=0 <1.38.1-r0
- Alpine:v3.13: `libuv` — affected >=0 <1.39.0-r0
- Alpine:v3.14: `libuv` — affected >=0 <1.39.0-r0
- Alpine:v3.15: `libuv` — affected >=0 <1.39.0-r0
- Alpine:v3.16: `libuv` — affected >=0 <1.39.0-r0
- Alpine:v3.17: `libuv` — affected >=0 <1.39.0-r0
- Alpine:v3.18: `libuv` — affected >=0 <1.39.0-r0
- Alpine:v3.19: `libuv` — affected >=0 <1.39.0-r0
- Alpine:v3.20: `libuv` — affected >=0 <1.39.0-r0
- Alpine:v3.21: `libuv` — affected >=0 <1.39.0-r0
- Alpine:v3.22: `libuv` — affected >=0 <1.39.0-r0
- Alpine:v3.23: `libuv` — affected >=0 <1.39.0-r0
- Alpine:v3.24: `libuv` — affected >=0 <1.39.0-r0
- Alpine:v3.11: `nodejs` — affected >=0 <12.20.1-r0
- Alpine:v3.12: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.13: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.14: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.15: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.16: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.17: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.18: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.19: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.20: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.21: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.22: `nodejs` — affected >=0 <12.18.4-r0

## Details
The implementation of realpath in libuv < 10.22.1, < 12.18.4, and < 14.9.0 used within Node.js incorrectly determined the buffer size which can result in a buffer overflow if the resolved path is longer than 256 bytes.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8252
