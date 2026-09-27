# [H] ntop nDPI before 6.0 Heap Buffer Overflow via ndpi_json_string_escape

## Summary
Severity: High
Advisory: CVE-2026-86098
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-86098
Type: osv

## Details
ntop nDPI versions before 6.0 contain a heap buffer overflow vulnerability in the ndpi_json_string_escape function that writes beyond caller-supplied buffer boundaries. Attackers can trigger the overflow by supplying crafted network packet data including TLS SNI, HTTP headers, or DNS names that reach the vulnerable function, causing heap corruption.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86098.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86098
- https://www.vulncheck.com/advisories/ntop-ndpi-before-6.0-heap-buffer-overflow-via-ndpi-json-string-escape
- https://github.com/ntop/nDPI/commit/94e82c1de12323d992895830231865736a8abf2c
- https://github.com/ntop/nDPI
- https://github.com/ntop/nDPI/blob/5.0/src/lib/ndpi_serializer.c
