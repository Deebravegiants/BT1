# [H] ALPINE-CVE-2025-0665

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-0665
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2025-02-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-0665
Type: osv

## Affected
- Alpine:v3.18: `curl` — affected >=0 <8.12.0-r0
- Alpine:v3.19: `curl` — affected >=0 <8.12.0-r0
- Alpine:v3.20: `curl` — affected >=0 <8.12.0-r0
- Alpine:v3.21: `curl` — affected >=0 <8.12.0-r0
- Alpine:v3.22: `curl` — affected >=0 <8.12.0-r0
- Alpine:v3.23: `curl` — affected >=0 <8.12.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.12.0-r0

## Details
libcurl would wrongly close the same eventfd file descriptor twice when taking
down a connection channel after having completed a threaded name resolve.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-0665
