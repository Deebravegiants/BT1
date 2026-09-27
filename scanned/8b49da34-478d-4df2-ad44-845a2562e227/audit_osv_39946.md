# [H] CVE-2026-48691

## Summary
Severity: High
Advisory: CVE-2026-48691
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-48691
Type: osv

## Details
FastNetMon Community Edition through 1.2.9 contains an integer overflow in the BGP AS_PATH attribute encoder. In src/bgp_protocol.hpp, the IPv4UnicastAnnounce::get_attributes() function computes attribute_length as 'sizeof(bgp_as_path_segment_element_t) + this->as_path_asns.size() * sizeof(uint32_t)' and stores it in a uint8_t field (line 600-605). Since uint8_t can only hold values 0-255, an AS_PATH containing more than 63 ASNs (2 + 64*4 = 258 > 255) causes silent truncation. The truncated length is used for buffer sizing, while the actual data written is the full untruncated amount, resulting in a heap buffer overflow. Similarly, the path_segment_length field at line 621 is also uint8_t, truncating with more than 255 ASNs.

## References
- https://github.com/pavel-odintsov/fastnetmon/blob/master/src/bgp_protocol.hpp
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48691.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48691
- https://github.com/pavel-odintsov/fastnetmon
- https://lorikeetsecurity.com/blog/fastnetmon-cve-2026-48691-bgp-as-path-overflow
