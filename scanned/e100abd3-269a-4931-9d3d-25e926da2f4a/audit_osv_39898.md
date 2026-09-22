# [C] CVE-2026-48137

## Summary
Severity: Critical
Advisory: CVE-2026-48137
Aliases: GHSA-ww59-ghm9-mm63
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-48137
Type: osv

## Details
There is an untrusted pointer dereference vulnerability in the NI grpc-device sideband streaming API that may allow an attacker to cause an arbitrary memory dereference, potentially resulting in remote code execution.  Successful exploitation requires an attacker  to supply a specially crafted Moniker protobuf message.  This affects NI grpc-device 2.17.0 and prior versions.

## References
- https://github.com/ni/grpc-device/security/advisories/GHSA-ww59-ghm9-mm63
- https://www.ni.com/en/support/security/available-critical-and-security-updates-for-ni-software/2026/multiple-vulnerabilities-in-ni-grpc-device-server.html
