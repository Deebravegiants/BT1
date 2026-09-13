# [H] ALPINE-CVE-2019-9513

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-9513
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-9513
Type: osv

## Affected
- Alpine:v3.10: `nghttp2` — affected >=0 <1.39.2-r0
- Alpine:v3.11: `nghttp2` — affected >=0 <1.39.2-r0
- Alpine:v3.12: `nghttp2` — affected >=0 <1.39.2-r0
- Alpine:v3.13: `nghttp2` — affected >=0 <1.39.2-r0
- Alpine:v3.14: `nghttp2` — affected >=0 <1.39.2-r0
- Alpine:v3.15: `nghttp2` — affected >=0 <1.39.2-r0
- Alpine:v3.16: `nghttp2` — affected >=0 <1.39.2-r0
- Alpine:v3.17: `nghttp2` — affected >=0 <1.39.2-r0
- Alpine:v3.18: `nghttp2` — affected >=0 <1.39.2-r0
- Alpine:v3.19: `nghttp2` — affected >=0 <1.39.2-r0
- Alpine:v3.20: `nghttp2` — affected >=0 <1.39.2-r0
- Alpine:v3.21: `nghttp2` — affected >=0 <1.39.2-r0
- Alpine:v3.22: `nghttp2` — affected >=0 <1.39.2-r0
- Alpine:v3.23: `nghttp2` — affected >=0 <1.39.2-r0
- Alpine:v3.24: `nghttp2` — affected >=0 <1.39.2-r0
- Alpine:v3.7: `nghttp2` — affected >=0 <1.39.2-r0
- Alpine:v3.8: `nghttp2` — affected >=0 <1.39.2-r0
- Alpine:v3.9: `nghttp2` — affected >=0 <1.35.1-r1
- Alpine:v3.10: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.11: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.12: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.13: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.14: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.15: `nginx` — affected >=1.9.5 <1.16.1-r0
- Alpine:v3.16: `nginx` — affected >=1.9.5 <1.16.1-r0

## Details
Some HTTP/2 implementations are vulnerable to resource loops, potentially leading to a denial of service. The attacker creates multiple request streams and continually shuffles the priority of the streams in a way that causes substantial churn to the priority tree. This can consume excess CPU.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-9513
