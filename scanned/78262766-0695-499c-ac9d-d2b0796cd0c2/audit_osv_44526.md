# [M] xmldom: requireWellFormed DocType publicId/systemId validation is bypassable via an embedded line terminator

## Summary
Severity: Medium
Advisory: CVE-2026-83618
Aliases: GHSA-vr34-hp96-76pp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-83618
Type: osv

## Details
xmldom is a pure JavaScript W3C standard-based (XML DOM Level 2 Core) DOMParser and XMLSerializer module. From 0.9.10 until 0.9.12, the requireWellFormed: true serializer validates DocumentType.publicId and DocumentType.systemId with PubidLiteral_match and SystemLiteral_match expressions produced by reg() in lib/grammar.js, which inherit the multiline flag. A complete valid literal on the first line can therefore satisfy the matcher while U+000A, U+000D, U+2028, or U+2029 and breakout markup remain in the emitted <!DOCTYPE ...> declaration. This bypasses the strict-serialization mitigation for the earlier DocumentType injection advisory; creation and direct property assignment remain unvalidated by design. This issue is fixed in @xmldom/xmldom version 0.9.12.

## References
- https://github.com/xmldom/xmldom/releases/tag/0.9.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/83xxx/CVE-2026-83618.json
- https://github.com/xmldom/xmldom/security/advisories/GHSA-vr34-hp96-76pp
- https://nvd.nist.gov/vuln/detail/CVE-2026-83618
- https://github.com/xmldom/xmldom/commit/7b2ec67e1750daadd0bb06c92e875e726544a362
- https://github.com/xmldom/xmldom/pull/1071
