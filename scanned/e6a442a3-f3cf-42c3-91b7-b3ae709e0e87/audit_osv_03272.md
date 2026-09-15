# [M] ALPINE-CVE-2025-35979

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-35979
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-35979
Type: osv

## Affected
- Alpine:v3.20: `intel-ucode` — affected >=0 <20260512-r0
- Alpine:v3.21: `intel-ucode` — affected >=0 <20260512-r0
- Alpine:v3.22: `intel-ucode` — affected >=0 <20260512-r0
- Alpine:v3.23: `intel-ucode` — affected >=0 <20260512-r0
- Alpine:v3.24: `intel-ucode` — affected >=0 <20260512-r0

## Details
Exposure of sensitive information caused by shared microarchitectural predictor state that influences transient execution for some Intel(R) Processors within VMX non-root (guest) operation may allow an information disclosure. Unprivileged software adversary with an authenticated user combined with a high complexity attack may enable data exposure. This result may potentially occur via local access when attack requirements are present without special internal knowledge and requires no user interaction. The potential vulnerability may impact the confidentiality (high), integrity (none) and availability (none) of the vulnerable system, resulting in subsequent system confidentiality (high), integrity (none) and availability (none) impacts.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-35979
