# [M] ALPINE-CVE-2025-4516

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-4516
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2025-05-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-4516
Type: osv

## Affected
- Alpine:v3.18: `python3` — affected >=0 <3.11.12-r1
- Alpine:v3.19: `python3` — affected >=0 <3.11.12-r1
- Alpine:v3.20: `python3` — affected >=0 <3.12.10-r1
- Alpine:v3.21: `python3` — affected >=0 <3.12.10-r1
- Alpine:v3.22: `python3` — affected >=0 <3.12.10-r1
- Alpine:v3.23: `python3` — affected >=0 <3.12.10-r1
- Alpine:v3.24: `python3` — affected >=0 <3.12.10-r1

## Details
There is an issue in CPython when using `bytes.decode("unicode_escape", error="ignore|replace")`. If you are not using the "unicode_escape" encoding or an error handler your usage is not affected. To work-around this issue you may stop using the error= handler and instead wrap the bytes.decode() call in a try-except catching the DecodeError.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-4516
