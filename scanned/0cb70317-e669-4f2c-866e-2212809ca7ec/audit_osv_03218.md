# [H] ALPINE-CVE-2025-22889

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-22889
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2025-08-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-22889
Type: osv

## Affected
- Alpine:v3.19: `intel-ucode` — affected >=0 <20250812-r0
- Alpine:v3.20: `intel-ucode` — affected >=0 <20250812-r0
- Alpine:v3.21: `intel-ucode` — affected >=0 <20250812-r0
- Alpine:v3.22: `intel-ucode` — affected >=0 <20250812-r0
- Alpine:v3.23: `intel-ucode` — affected >=0 <20250812-r0
- Alpine:v3.24: `intel-ucode` — affected >=0 <20250812-r0

## Details
Improper handling of overlap between protected memory ranges for some Intel(R) Xeon(R) 6 processor with Intel(R) TDX may allow a privileged user to potentially enable escalation of privilege via local access.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-22889
