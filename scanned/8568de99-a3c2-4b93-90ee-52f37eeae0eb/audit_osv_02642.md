# [H] ALPINE-CVE-2022-40468

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-40468
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-09-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-40468
Type: osv

## Affected
- Alpine:v3.16: `tinyproxy` — affected >=0 <1.11.1-r2
- Alpine:v3.17: `tinyproxy` — affected >=0 <1.11.1-r2
- Alpine:v3.18: `tinyproxy` — affected >=0 <1.11.1-r2
- Alpine:v3.19: `tinyproxy` — affected >=0 <1.11.1-r2
- Alpine:v3.20: `tinyproxy` — affected >=0 <1.11.1-r2
- Alpine:v3.21: `tinyproxy` — affected >=0 <1.11.1-r2
- Alpine:v3.22: `tinyproxy` — affected >=0 <1.11.1-r2
- Alpine:v3.23: `tinyproxy` — affected >=0 <1.11.1-r2
- Alpine:v3.24: `tinyproxy` — affected >=0 <1.11.1-r2

## Details
Potential leak of left-over heap data if custom error page templates containing special non-standard variables are used. Tinyproxy commit 84f203f and earlier use uninitialized buffers in process_request() function.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-40468
