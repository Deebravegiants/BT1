# [M] libyang - Heap Use-After-Free Write in XML Metadata Parsing

## Summary
Severity: Medium
Advisory: CVE-2026-41401
Aliases: GHSA-9f49-8x56-jmjc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-41401
Type: osv

## Details
libyang before 5.2.6 contains a heap use-after-free write vulnerability in lyd_parser_set_data_flags that incorrectly updates metadata list pointers when freeing non-head default metadata entries. Attackers can trigger this vulnerability by submitting crafted YANG XML documents with specific metadata attributes to applications parsing untrusted XML data, causing process crashes or potential code execution.

## References
- https://github.com/CESNET/libyang/security/advisories/GHSA-9f49-8x56-jmjc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41401.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41401
- https://red.anthropic.com/2026/cvd/findings/ANT-2026-TZQ1KH7E
- https://www.vulncheck.com/advisories/libyang-heap-use-after-free-write-in-xml-metadata-parsing
- https://github.com/CESNET/libyang/commit/6b5ed47ee674fbe86b31bbebc4ff26889aeff38c
