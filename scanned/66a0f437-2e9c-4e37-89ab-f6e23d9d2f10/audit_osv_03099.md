# [M] ALPINE-CVE-2024-43420

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-43420
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2025-05-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-43420
Type: osv

## Affected
- Alpine:v3.18: `intel-ucode` — affected >=0 <20250512-r0
- Alpine:v3.19: `intel-ucode` — affected >=0 <20250512-r0
- Alpine:v3.20: `intel-ucode` — affected >=0 <20250512-r0
- Alpine:v3.21: `intel-ucode` — affected >=0 <20250512-r0
- Alpine:v3.22: `intel-ucode` — affected >=0 <20250512-r0
- Alpine:v3.23: `intel-ucode` — affected >=0 <20250512-r0
- Alpine:v3.24: `intel-ucode` — affected >=0 <20250512-r0

## Details
Exposure of sensitive information caused by shared microarchitectural predictor state that influences transient execution for some Intel Atom(R) processors may allow an authenticated user to potentially enable information disclosure via local access.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-43420
