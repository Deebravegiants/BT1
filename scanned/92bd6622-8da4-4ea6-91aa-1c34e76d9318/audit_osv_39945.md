# [H] CVE-2026-48690

## Summary
Severity: High
Advisory: CVE-2026-48690
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-48690
Type: osv

## Details
FastNetMon Community Edition through 1.2.9 contains an integer overflow vulnerability in the packet capture buffer allocation. In src/packet_storage.hpp, the allocate_buffer() function computes memory_size_in_bytes as 'buffer_size_in_packets * (max_captured_packet_size + sizeof(fastnetmon_pcap_pkthdr_t)) + sizeof(fastnetmon_pcap_file_header_t)' using unsigned int (32-bit) arithmetic. With max_captured_packet_size=1500 and sizeof(fastnetmon_pcap_pkthdr_t)=16, each packet requires approximately 1516 bytes. If buffer_size_in_packets exceeds approximately 2,832,542, the multiplication overflows, resulting in a much smaller allocation than expected. Subsequent write_packet() calls then write past the allocated buffer, causing heap corruption. The buffer_size_in_packets value is derived from the ban_details_records_count configuration parameter, which is parsed using atoi() with no overflow checking.

## References
- https://github.com/pavel-odintsov/fastnetmon/blob/master/src/packet_storage.hpp
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48690.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48690
- https://github.com/pavel-odintsov/fastnetmon
- https://lorikeetsecurity.com/blog/fastnetmon-cve-2026-48690-packet-storage-integer-overflow
