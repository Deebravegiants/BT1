# [M] BACnet Stack: Out-of-Bounds Read in WritePropertyMultiple Decoder via Deprecated Tag Parser

## Summary
Severity: Medium
Advisory: CVE-2026-41475
Aliases: GHSA-cvv4-v3g6-4jmv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-41475
Type: osv

## Details
BACnet Stack is a BACnet open source protocol stack C library for embedded systems. Prior to 1.4.3, an out-of-bounds read vulnerability in bacnet-stack's WritePropertyMultiple service decoder allows unauthenticated remote attackers to read past allocated buffer boundaries by sending a truncated WPM request. The vulnerability stems from wpm_decode_object_property() calling the deprecated decode_tag_number_and_value() function, which performs no bounds checking on the input buffer. A crafted BACnet/IP packet with a truncated property payload causes the decoder to read 1-7 bytes past the end of the buffer, leading to crashes or information disclosure on embedded BACnet devices. This vulnerability is fixed in 1.4.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41475.json
- https://github.com/bacnet-stack/bacnet-stack/security/advisories/GHSA-cvv4-v3g6-4jmv
- https://nvd.nist.gov/vuln/detail/CVE-2026-41475
