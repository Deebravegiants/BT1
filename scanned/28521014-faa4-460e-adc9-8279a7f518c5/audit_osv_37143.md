# [M] FRRouting < 10.5.3 Integer Overflow in OSPF TLV Parser Functions

## Summary
Severity: Medium
Advisory: CVE-2026-28532
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/CVE-2026-28532
Type: osv

## Details
FRRouting before 10.5.3 contains an integer overflow vulnerability in seven OSPF Traffic Engineering and Segment Routing TLV parser functions where a uint16_t accumulator variable truncates uint32_t values returned by the TLV_SIZE() macro, causing the loop termination condition to fail while pointer advancement continues unchecked. Attackers with an established OSPF adjacency can send a crafted LS Update packet with a malicious Type 10 or Type 11 Opaque LSA to trigger out-of-bounds memory reads and crash all affected routers in the OSPF area or autonomous system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28532.json
- https://github.com/FRRouting/frr/releases/tag/frr-10.5.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-28532
- https://www.vulncheck.com/advisories/frrouting-integer-overflow-in-ospf-tlv-parser-functions
- https://github.com/FRRouting/frr/pull/21002
- https://github.com/FRRouting/frr/commit/f098decf02987fbf1c891766c1516ac832adadfd
