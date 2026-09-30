# [M] BACnet Stack: Off-by-One Out-of-Bounds Read in ReadPropertyMultiple Object ID Decoder

## Summary
Severity: Medium
Advisory: CVE-2026-41502
Aliases: GHSA-7545-3fpx-4xw3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-41502
Type: osv

## Details
BACnet Stack is a BACnet open source protocol stack C library for embedded systems. Prior to 1.4.3, an off-by-one out-of-bounds read vulnerability in bacnet-stack's ReadPropertyMultiple service decoder allows unauthenticated remote attackers to read one byte past an allocated buffer boundary by sending a crafted RPM request with a truncated object identifier. The vulnerability is in rpm_decode_object_id(), which checks apdu_len < 5 but then accesses all 6 byte positions (indices 0-5) — consuming 1 byte for the context tag, 4 bytes for the object ID, then reading apdu[5] for the opening tag check. A 5-byte input passes the length check but causes a 1-byte OOB read, leading to crashes on embedded BACnet devices. The vulnerability exists in src/bacnet/rpm.c and affects any deployment that enables the ReadPropertyMultiple confirmed service handler (enabled by default in the reference server). This vulnerability is fixed in 1.4.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41502.json
- https://github.com/bacnet-stack/bacnet-stack/security/advisories/GHSA-7545-3fpx-4xw3
- https://nvd.nist.gov/vuln/detail/CVE-2026-41502
