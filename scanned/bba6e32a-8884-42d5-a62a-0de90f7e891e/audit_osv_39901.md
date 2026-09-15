# [M] CVE-2026-48140

## Summary
Severity: Medium
Advisory: CVE-2026-48140
Aliases: GHSA-prfr-q8h3-mqxv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-48140
Type: osv

## Details
There is an unchecked enum cast vulnerability in NI grpc-device BeginSidebandStream that may allow an attacker to trigger invalid enum states and undefined behavior, potentially resulting in a denial of service. Successful exploitation requires an attacker to supply a specially crafted message containing an out-of-range value. This affects NI grpc-device 2.17.0 and prior versions.

## References
- https://github.com/ni/grpc-device/security/advisories/GHSA-prfr-q8h3-mqxv
- https://www.ni.com/en/support/security/available-critical-and-security-updates-for-ni-software/2026/multiple-vulnerabilities-in-ni-grpc-device-server.html
