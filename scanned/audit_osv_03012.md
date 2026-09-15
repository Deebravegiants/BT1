# [C] ALPINE-CVE-2024-24853

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-24853
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:H/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2024-08-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-24853
Type: osv

## Affected
- Alpine:v3.17: `intel-ucode` — affected >=0 <20240813-r0
- Alpine:v3.18: `intel-ucode` — affected >=0 <20240813-r0
- Alpine:v3.19: `intel-ucode` — affected >=0 <20240813-r0
- Alpine:v3.20: `intel-ucode` — affected >=0 <20260210-r0
- Alpine:v3.21: `intel-ucode` — affected >=0 <20260210-r0
- Alpine:v3.22: `intel-ucode` — affected >=0 <20260210-r0
- Alpine:v3.23: `intel-ucode` — affected >=0 <20260210-r0
- Alpine:v3.24: `intel-ucode` — affected >=0 <20260210-r0

## Details
Incorrect behavior order in transition between executive monitor and SMI transfer monitor (STM) in some Intel(R) Processor may allow a privileged user to potentially enable escalation of privilege via local access.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-24853
