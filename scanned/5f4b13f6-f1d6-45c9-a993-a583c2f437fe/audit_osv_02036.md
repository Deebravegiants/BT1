# [M] ALPINE-CVE-2020-8927

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-8927
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2020-09-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8927
Type: osv

## Affected
- Alpine:v3.12: `brotli` — affected >=0 <1.0.9-r0
- Alpine:v3.13: `brotli` — affected >=0 <1.0.9-r0
- Alpine:v3.14: `brotli` — affected >=0 <1.0.9-r0
- Alpine:v3.15: `brotli` — affected >=0 <1.0.9-r0
- Alpine:v3.16: `brotli` — affected >=0 <1.0.9-r0
- Alpine:v3.17: `brotli` — affected >=0 <1.0.9-r0
- Alpine:v3.18: `brotli` — affected >=0 <1.0.9-r0
- Alpine:v3.19: `brotli` — affected >=0 <1.0.9-r0
- Alpine:v3.20: `brotli` — affected >=0 <1.0.9-r0
- Alpine:v3.21: `brotli` — affected >=0 <1.0.9-r0
- Alpine:v3.22: `brotli` — affected >=0 <1.0.9-r0
- Alpine:v3.23: `brotli` — affected >=0 <1.0.9-r0
- Alpine:v3.24: `brotli` — affected >=0 <1.0.9-r0

## Details
A buffer overflow exists in the Brotli library versions prior to 1.0.8 where an attacker controlling the input length of a "one-shot" decompression request to a script can trigger a crash, which happens when copying over chunks of data larger than 2 GiB. It is recommended to update your Brotli library to 1.0.8 or later. If one cannot update, we recommend to use the "streaming" API as opposed to the "one-shot" API, and impose chunk size limits.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8927
