# [M] YaCy Search Server through 1.941 XML External Entity Injection via Parsers

## Summary
Severity: Medium
Advisory: CVE-2026-82880
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-82880
Type: osv

## Details
YaCy Search Server through 1.941 contains an XML external entity injection vulnerability in SVG, FreeMind, and OpenSearch parsers that fail to disable external entity resolution. Attackers can publish malicious documents with DOCTYPE declarations containing SYSTEM entities pointing to local files, causing the crawler to exfiltrate file contents into the searchable index.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82880.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82880
- https://www.vulncheck.com/advisories/yacy-search-server-through-1.941-xml-external-entity-injection-via-parsers
- https://github.com/yacy/yacy_search_server/issues/818
- https://github.com/yacy/yacy_search_server/commit/3c3a307e8b7a0ebbc4d1e6b10898b52e15c0cd44
- https://github.com/yacy/yacy_search_server
- https://github.com/yacy/yacy_search_server/blob/Release_1.941/source/net/yacy/document/parser/images/svgParser.java#L72
- https://github.com/yacy/yacy_search_server/blob/Release_1.941/source/net/yacy/document/parser/mmParser.java#L66
- https://github.com/yacy/yacy_search_server/blob/Release_1.941/source/net/yacy/document/parser/xml/opensearchdescriptionReader.java#L119
