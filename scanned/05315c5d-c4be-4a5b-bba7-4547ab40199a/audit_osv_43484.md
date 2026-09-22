# [M] TIER IV Nebula 1.2.0 Heap Out-of-Bounds Read via VLP32 UDP Decoder

## Summary
Severity: Medium
Advisory: CVE-2026-74238
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74238
Type: osv

## Details
TIER IV Nebula through 1.2.0 contains an out-of-bounds read vulnerability in the Vlp32Decoder::unpack() function that allows unauthenticated remote attackers to cause the decoder to read past the end of a received UDP buffer into adjacent heap memory by sending a short UDP datagram. Attackers can send a malformed datagram to the Velodyne UDP sensor port, which lacks sender-address restrictions present in other drivers, causing fabricated points derived from heap memory contents to be silently published into downstream PointCloud2 messages consumed by Autoware nodes.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74238.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74238
- https://www.vulncheck.com/advisories/tier-iv-nebula-heap-out-of-bounds-read-via-vlp32-udp-decoder
- https://github.com/tier4/nebula/issues/488
- https://github.com/tier4/nebula
