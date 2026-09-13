# [C] ALPINE-CVE-2024-23918

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-23918
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2024-11-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-23918
Type: osv

## Affected
- Alpine:v3.17: `intel-ucode` — affected >=0 <20241112-r0
- Alpine:v3.18: `intel-ucode` — affected >=0 <20241112-r0
- Alpine:v3.19: `intel-ucode` — affected >=0 <20241112-r0
- Alpine:v3.20: `intel-ucode` — affected >=0 <20241112-r0
- Alpine:v3.21: `intel-ucode` — affected >=0 <20241112-r0
- Alpine:v3.22: `intel-ucode` — affected >=0 <20241112-r0
- Alpine:v3.23: `intel-ucode` — affected >=0 <20241112-r0
- Alpine:v3.24: `intel-ucode` — affected >=0 <20241112-r0

## Details
Improper conditions check in some Intel(R) Xeon(R) processor memory controller configurations when using Intel(R) SGX may allow a privileged user to potentially enable escalation of privilege via local access.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-23918
