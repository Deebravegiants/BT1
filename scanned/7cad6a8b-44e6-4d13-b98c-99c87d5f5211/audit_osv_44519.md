# [M] xmldom: Creation-time XML Name/QName validation is bypassable via an embedded line terminator, allowing injection on the default serialization path

## Summary
Severity: Medium
Advisory: CVE-2026-83609
Aliases: GHSA-3px3-54cx-rmw9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-83609
Type: osv

## Details
xmldom is a pure JavaScript W3C standard-based (XML DOM Level 2 Core) DOMParser and XMLSerializer module. From 0.9.0 until 0.9.12, the shared reg() builder in lib/grammar.js compiles the anchored QName_exact validator with the multiline flag, so ^ and $ validate only one line instead of the complete name. createElementNS, createAttributeNS, createDocumentType, and createAttribute consequently accept a malformed XML name whose first line is valid and whose later text injects markup when serialized through either the default path or requireWellFormed: true. The triggering ECMAScript line terminators are U+000A, U+000D, U+2028, and U+2029. This issue is fixed in @xmldom/xmldom version 0.9.12.

## References
- https://github.com/xmldom/xmldom/releases/tag/0.9.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/83xxx/CVE-2026-83609.json
- https://github.com/xmldom/xmldom/security/advisories/GHSA-3px3-54cx-rmw9
- https://nvd.nist.gov/vuln/detail/CVE-2026-83609
- https://github.com/xmldom/xmldom/commit/7b2ec67e1750daadd0bb06c92e875e726544a362
- https://github.com/xmldom/xmldom/pull/1071
