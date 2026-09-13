# [M] CVE-2026-79707

## Summary
Severity: Medium
Advisory: CVE-2026-79707
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:Amber)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-79707
Type: osv

## Details
A Path Traversal vulnerability in the builder endpoint in Google Cloud Agent Development Kit (ADK) versions 1.9.0 through 1.21.0 on Python allows an unauthenticated remote attacker to read arbitrary files using a crafted file_path query parameter.

## References
- https://github.com/google/adk-python/blob/main/CHANGELOG.md#1220-2026-01-08
- https://github.com/google/adk-python/commit/6f259f08b3c45ad6050b8a93c9bd85913451ece6
