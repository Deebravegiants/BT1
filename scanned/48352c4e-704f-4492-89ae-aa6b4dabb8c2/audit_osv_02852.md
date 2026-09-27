# [H] ALPINE-CVE-2023-38039

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-38039
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-38039
Type: osv

## Affected
- Alpine:v3.15: `curl` — affected >=7.84.0 <8.3.0-r0
- Alpine:v3.16: `curl` — affected >=7.84.0 <8.3.0-r0
- Alpine:v3.17: `curl` — affected >=7.84.0 <8.3.0-r0
- Alpine:v3.18: `curl` — affected >=7.84.0 <8.3.0-r0
- Alpine:v3.19: `curl` — affected >=7.84.0 <8.3.0-r0
- Alpine:v3.20: `curl` — affected >=7.84.0 <8.3.0-r0
- Alpine:v3.21: `curl` — affected >=7.84.0 <8.3.0-r0
- Alpine:v3.22: `curl` — affected >=7.84.0 <8.3.0-r0
- Alpine:v3.23: `curl` — affected >=7.84.0 <8.3.0-r0
- Alpine:v3.24: `curl` — affected >=7.84.0 <8.3.0-r0

## Details
When curl retrieves an HTTP response, it stores the incoming headers so that
they can be accessed later via the libcurl headers API.

However, curl did not have a limit in how many or how large headers it would
accept in a response, allowing a malicious server to stream an endless series
of headers and eventually cause curl to run out of heap memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-38039
