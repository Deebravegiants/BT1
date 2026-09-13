# [M] CVE-2026-48139

## Summary
Severity: Medium
Advisory: CVE-2026-48139
Aliases: GHSA-7vg9-5c74-289x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-48139
Type: osv

## Details
There is a NULL pointer dereference vulnerability in NI grpc-device in the data moniker service that may allow an attacker to cause a denial of service by triggering a crash.  Successful exploitation requires an attacker to provide an unknown value to the data moniker service. This affects NI grpc-device 2.17.0 and prior versions.

## References
- https://github.com/ni/grpc-device/security/advisories/GHSA-7vg9-5c74-289x
- https://www.ni.com/en/support/security/available-critical-and-security-updates-for-ni-software/2026/multiple-vulnerabilities-in-ni-grpc-device-server.html
