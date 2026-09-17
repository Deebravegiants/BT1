# [M] ALPINE-CVE-2020-29362

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-29362
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-12-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-29362
Type: osv

## Affected
- Alpine:v3.10: `p11-kit` — affected >=0.23.6 <0.23.16.1-r1
- Alpine:v3.11: `p11-kit` — affected >=0.23.6 <0.23.18.1-r1
- Alpine:v3.12: `p11-kit` — affected >=0.23.6 <0.23.22-r0
- Alpine:v3.13: `p11-kit` — affected >=0.23.6 <0.23.22-r0
- Alpine:v3.14: `p11-kit` — affected >=0.23.6 <0.23.22-r0
- Alpine:v3.15: `p11-kit` — affected >=0.23.6 <0.23.22-r0
- Alpine:v3.16: `p11-kit` — affected >=0.23.6 <0.23.22-r0
- Alpine:v3.17: `p11-kit` — affected >=0.23.6 <0.23.22-r0
- Alpine:v3.18: `p11-kit` — affected >=0.23.6 <0.23.22-r0
- Alpine:v3.19: `p11-kit` — affected >=0.23.6 <0.23.22-r0
- Alpine:v3.20: `p11-kit` — affected >=0.23.6 <0.23.22-r0
- Alpine:v3.21: `p11-kit` — affected >=0.23.6 <0.23.22-r0
- Alpine:v3.22: `p11-kit` — affected >=0.23.6 <0.23.22-r0
- Alpine:v3.23: `p11-kit` — affected >=0.23.6 <0.23.22-r0
- Alpine:v3.24: `p11-kit` — affected >=0.23.6 <0.23.22-r0

## Details
An issue was discovered in p11-kit 0.21.1 through 0.23.21. A heap-based buffer over-read has been discovered in the RPC protocol used by thep11-kit server/remote commands and the client library. When the remote entity supplies a byte array through a serialized PKCS#11 function call, the receiving entity may allow the reading of up to 4 bytes of memory past the heap allocation.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-29362
