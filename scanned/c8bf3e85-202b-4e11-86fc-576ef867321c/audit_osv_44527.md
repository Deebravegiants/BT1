# [M] xmldom: End-tag Whitespace-Trim Regex ReDoS — quadratic backtracking in the 0.8.x end-tag parser

## Summary
Severity: Medium
Advisory: CVE-2026-83619
Aliases: GHSA-x4fp-j954-r2f4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-83619
Type: osv

## Details
xmldom is a pure JavaScript W3C standard-based (XML DOM Level 2 Core) DOMParser and XMLSerializer module. From 0.7.0 until 0.8.15, the release-0.8.x parser in lib/sax.js trims captured end-tag names with the unanchored global expression /[ \t\n\r]+$/g. For an end tag containing a long whitespace run followed by a non-whitespace character, the expression retries from each possible starting position and backtracks quadratically before failing its end anchor. DOMParser.parseFromString() reaches the path under default options, allowing a small unauthenticated XML input to stall the Node.js event loop; the 0.9.x and unscoped npm lines do not contain this expression. This issue is fixed in @xmldom/xmldom version 0.8.15.

## References
- https://github.com/xmldom/xmldom/releases/tag/0.8.15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/83xxx/CVE-2026-83619.json
- https://github.com/xmldom/xmldom/security/advisories/GHSA-x4fp-j954-r2f4
- https://nvd.nist.gov/vuln/detail/CVE-2026-83619
- https://github.com/xmldom/xmldom/commit/3abb0934f5a8a84d83a1f9cde0f2bd04c08b2a09
- https://github.com/xmldom/xmldom/pull/1072
