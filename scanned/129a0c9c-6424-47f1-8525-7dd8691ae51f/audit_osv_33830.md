# [H] CVE-2025-51005

## Summary
Severity: High
Advisory: CVE-2025-51005
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-51005
Type: osv

## Details
A heap-buffer-overflow vulnerability exists in the tcpliveplay utility of the tcpreplay-4.5.1. When a crafted pcap file is processed, the program incorrectly handles memory in the checksum calculation logic at do_checksum_math_liveplay in tcpliveplay.c, leading to a possible denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/51xxx/CVE-2025-51005.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-51005
- https://github.com/appneta/tcpreplay/issues/925
- https://github.com/sy460129/CVE-2025-51005
