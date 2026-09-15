# [H] CVE-2026-9142

## Summary
Severity: High
Advisory: CVE-2026-9142
Aliases: GHSA-fhhw-37q8-6562
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-9142
Type: osv

## Details
There is an insecure default credentials vulnerability in NI grpc-device when TLS configuration is not present and the server is bound beyond loopback.  This may allow an unauthenticated user access to the server on the local network.  This affects NI grpc-device 2.17.0 and prior versions.

## References
- https://github.com/ni/grpc-device/security/advisories/GHSA-fhhw-37q8-6562
- https://www.ni.com/en/support/security/available-critical-and-security-updates-for-ni-software/2026/multiple-vulnerabilities-in-ni-grpc-device-server.html
