# [M] ALPINE-CVE-2026-20760

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-20760
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-20760
Type: osv

## Affected
- Alpine:v3.21: `intel-ucode` — affected >=0 <20260812-r0
- Alpine:v3.22: `intel-ucode` — affected >=0 <20260812-r0
- Alpine:v3.23: `intel-ucode` — affected >=0 <20260812-r0
- Alpine:v3.24: `intel-ucode` — affected >=0 <20260812-r0

## Details
Improper handling of overlap between protected memory ranges in some microcode for some Intel(R) Processors within Ring 0: Hypervisor may allow an escalation of privilege. Authorized adversary with a privileged user combined with a low complexity attack may enable escalation of privilege. This result may potentially occur via local access when attack requirements are not present without special internal knowledge and requires no user interaction. The potential vulnerability may impact the confidentiality (high), integrity (high) and availability (high) of the vulnerable system, resulting in subsequent system confidentiality (none), integrity (none) and availability (none) impacts.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-20760
