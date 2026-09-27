# [M] ALPINE-CVE-2025-65102

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-65102
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-65102
Type: osv

## Affected
- Alpine:v3.23: `pjproject` — affected >=0 <2.16.0-r0
- Alpine:v3.24: `pjproject` — affected >=0 <2.16.0-r0

## Details
PJSIP is a free and open source multimedia communication library. Prior to version 2.16, Opus PLC may zero-fill the input frame as long as the decoder ptime, while the input frame length, which is based on stream ptime, may be less than that. This issue affects PJSIP users who use the Opus audio codec in receiving direction. The vulnerability can lead to unexpected application termination due to a memory overwrite. This issue has been patched in version 2.16.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-65102
