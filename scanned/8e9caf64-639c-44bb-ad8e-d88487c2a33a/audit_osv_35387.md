# [M] Nokogiri before 1.18.8 Heap Buffer Under-read via XML Schema

## Summary
Severity: Medium
Advisory: CVE-2025-71346
Aliases: GHSA-5w6v-399v-w3cc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2025-71346
Type: osv

## Details
Nokogiri before 1.18.8 packages a vulnerable version of libxml2 (before 2.13.8) that contains a heap-based buffer under-read (CVE-2025-32415) in the xmlSchemaIDCFillNodeTables function in xmlschemas.c. The issue can be triggered when validating against an untrusted XML Schema, or when validating untrusted documents against trusted schemas that use xsd:keyref in combination with recursively defined types that have additional identity constraints. Upstream and MITRE rate this issue as low severity.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71346.json
- https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-5w6v-399v-w3cc
- https://nvd.nist.gov/vuln/detail/CVE-2025-71346
- https://www.vulncheck.com/advisories/nokogiri-before-heap-buffer-under-read-via-xml-schema
