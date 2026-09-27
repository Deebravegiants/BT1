# [M] CVE-2026-9143

## Summary
Severity: Medium
Advisory: CVE-2026-9143
Aliases: GHSA-rhh6-fvjv-8m84
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-9143
Type: osv

## Details
There is an incorrect conversion between numeric types vulnerability in NI grpc-device due to missing range checks in CodeGen.  This may silently discard high bits if a size value exceeded the target type's range. This affects NI grpc-device 2.17.0 and prior versions.

## References
- https://github.com/ni/grpc-device/security/advisories/GHSA-rhh6-fvjv-8m84
- https://www.ni.com/en/support/security/available-critical-and-security-updates-for-ni-software/2026/multiple-vulnerabilities-in-ni-grpc-device-server.html
