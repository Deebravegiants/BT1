# [H] ALPINE-CVE-2019-9514

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-9514
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-9514
Type: osv

## Affected
- Alpine:v3.10: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.11: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.12: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.13: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.14: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.15: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.16: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.17: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.18: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.19: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.20: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.21: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.22: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.23: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.24: `nodejs` — affected >=0 <10.16.3-r0
- Alpine:v3.9: `nodejs` — affected >=0 <10.16.3-r0

## Details
Some HTTP/2 implementations are vulnerable to a reset flood, potentially leading to a denial of service. The attacker opens a number of streams and sends an invalid request over each stream that should solicit a stream of RST_STREAM frames from the peer. Depending on how the peer queues the RST_STREAM frames, this can consume excess memory, CPU, or both.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-9514
