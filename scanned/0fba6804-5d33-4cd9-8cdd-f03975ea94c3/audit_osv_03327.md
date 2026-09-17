# [H] ALPINE-CVE-2025-5399

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-5399
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-06-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-5399
Type: osv

## Affected
- Alpine:v3.19: `curl` — affected >=8.13.0 <8.14.1-r0
- Alpine:v3.20: `curl` — affected >=8.13.0 <8.14.1-r0
- Alpine:v3.21: `curl` — affected >=8.13.0 <8.14.1-r0
- Alpine:v3.22: `curl` — affected >=8.13.0 <8.14.1-r0
- Alpine:v3.23: `curl` — affected >=8.13.0 <8.14.1-r0
- Alpine:v3.24: `curl` — affected >=8.13.0 <8.14.1-r0

## Details
Due to a mistake in libcurl's WebSocket code, a malicious server can send a
particularly crafted packet which makes libcurl get trapped in an endless
busy-loop.

There is no other way for the application to escape or exit this loop other
than killing the thread/process.

This might be used to DoS libcurl-using application.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-5399
