# [H] CVE-2026-48141

## Summary
Severity: High
Advisory: CVE-2026-48141
Aliases: GHSA-j4qc-5v3f-rf87
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-48141
Type: osv

## Details
There is a memory leak in NI grpc-device BeginSidebandStream that may result in denial of service due to memory exhaustion.  This affects NI grpc-device 2.17.0 and prior versions.

## References
- https://github.com/ni/grpc-device/security/advisories/GHSA-j4qc-5v3f-rf87
- https://www.ni.com/en/support/security/available-critical-and-security-updates-for-ni-software/2026/multiple-vulnerabilities-in-ni-grpc-device-server.html
