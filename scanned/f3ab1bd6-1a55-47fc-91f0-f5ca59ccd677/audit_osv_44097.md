# [C] CVE-2026-79696

## Summary
Severity: Critical
Advisory: CVE-2026-79696
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:Amber)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-79696
Type: osv

## Details
A Code Injection vulnerability in adk web in Google Cloud Agent Development Kit (ADK) for Python versions 2.0.0 through 2.6.0 on Python (OSS), Cloud Run, and GKE environments where pytest is installed allows an unauthenticated remote attacker to execute arbitrary code using a crafted test session replay.

## References
- https://github.com/google/adk-python/releases/tag/v2.7.0
- https://github.com/google/adk-python/commit/a16f6da3314b8dcd9925884cd6fc7fc9ffdd570d
