# [M] CVE-2025-2296

## Summary
Severity: Medium
Advisory: CVE-2025-2296
Aliases: GHSA-6pp6-cm5h-86g5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:H/VA:L/SC:L/SI:H/SA:L/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2025-2296
Type: osv

## Details
EDK2 contains a vulnerability in BIOS where an attacker may cause “ Improper Input Validation” by local access. Successful exploitation of this vulnerability could alter control flow in unexpected ways, potentially allowing arbitrary command execution and impacting Confidentiality, Integrity, and Availability.

## References
- https://github.com/tianocore/edk2/security/advisories/GHSA-6pp6-cm5h-86g5
