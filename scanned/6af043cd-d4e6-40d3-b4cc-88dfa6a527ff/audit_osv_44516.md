# [M] xmldom PI grammar regex ReDoS: quadratic backtracking on unterminated processing instructions

## Summary
Severity: Medium
Advisory: CVE-2026-83606
Aliases: GHSA-g53g-w8rj-fmg7
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-83606
Type: osv

## Details
xmldom is a pure JavaScript W3C standard-based (XML DOM Level 2 Core) DOMParser and XMLSerializer module. From 0.9.0-beta.9 until 0.9.11, the processing-instruction production in lib/grammar.js lets the greedy S+ separator and lazy Char*? data group repeatedly repartition a long whitespace tail when the required closing ?> is absent. Both parsePI and parseProcessingInstruction apply the expression to the entire remaining source, causing quadratic backtracking during DOMParser.parseFromString() under default options and allowing a small unauthenticated XML input to stall the Node.js event loop. This issue is fixed in @xmldom/xmldom version 0.9.11.

## References
- https://github.com/xmldom/xmldom/releases/tag/0.9.11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/83xxx/CVE-2026-83606.json
- https://github.com/xmldom/xmldom/security/advisories/GHSA-g53g-w8rj-fmg7
- https://nvd.nist.gov/vuln/detail/CVE-2026-83606
- https://github.com/xmldom/xmldom/commit/73df6b8bdbd86f904b9e8c3ab9c49aa54ef2802e
- https://github.com/xmldom/xmldom/pull/1039
