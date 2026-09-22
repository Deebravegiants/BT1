# [M] xmldom: requireWellFormed element/attribute name validation is bypassable via an embedded line terminator

## Summary
Severity: Medium
Advisory: CVE-2026-83617
Aliases: GHSA-jxjr-3g7g-3944
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-83617
Type: osv

## Details
xmldom is a pure JavaScript W3C standard-based (XML DOM Level 2 Core) DOMParser and XMLSerializer module. From 0.9.11 until 0.9.12, the requireWellFormed: true element and attribute name checks use the anchored QName_exact expression produced by reg() in lib/grammar.js, which inherits the multiline flag. A name with a valid first line followed by U+000A, U+000D, U+2028, or U+2029 and breakout markup therefore passes validation and is emitted verbatim in element start and end tags or attribute names. This bypasses the strict-serialization checks introduced for the earlier element-name and attribute-name injection advisories, while the default serialization path remains outside the strict guarantee. This issue is fixed in @xmldom/xmldom version 0.9.12.

## References
- https://github.com/xmldom/xmldom/releases/tag/0.9.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/83xxx/CVE-2026-83617.json
- https://github.com/xmldom/xmldom/security/advisories/GHSA-jxjr-3g7g-3944
- https://nvd.nist.gov/vuln/detail/CVE-2026-83617
- https://github.com/xmldom/xmldom/commit/7b2ec67e1750daadd0bb06c92e875e726544a362
- https://github.com/xmldom/xmldom/pull/1071
