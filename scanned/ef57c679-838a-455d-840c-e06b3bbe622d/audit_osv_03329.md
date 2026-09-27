# [M] ALPINE-CVE-2025-54350

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-54350
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-08-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-54350
Type: osv

## Affected
- Alpine:v3.22: `iperf3` — affected >=3.2 <3.19.1-r0
- Alpine:v3.23: `iperf3` — affected >=3.2 <3.19.1-r0
- Alpine:v3.24: `iperf3` — affected >=3.2 <3.19.1-r0

## Details
In iperf before 3.19.1, iperf_auth.c has a Base64Decode assertion failure and application exit upon a malformed authentication attempt.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-54350
