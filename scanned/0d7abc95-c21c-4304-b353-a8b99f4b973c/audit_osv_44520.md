# [M] xmldom: HTML raw-text closing-tag case mismatch causes output amplification

## Summary
Severity: Medium
Advisory: CVE-2026-83612
Aliases: GHSA-6mj3-qw4j-hgrw
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-83612
Type: osv

## Details
xmldom is a pure JavaScript W3C standard-based (XML DOM Level 2 Core) DOMParser and XMLSerializer module. From 0.9.0-beta.1 until 0.9.12, HTML-mode parsing through DOMParser.parseFromString() mishandles a mixed-case closing tag for the script, style, textarea, or title raw-text elements. parseHtmlSpecialContent, selected by isHTMLRawTextElement or isHTMLEscapableRawTextElement, uses a case-sensitive indexOf() and then calls substring() with a missing-close result of negative one, causing unstable parser progression and quadratic output amplification. A small untrusted text/html document can consequently consume disproportionate CPU and memory when parsed and serialized. This issue is fixed in @xmldom/xmldom version 0.9.12.

## References
- https://github.com/xmldom/xmldom/releases/tag/0.9.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/83xxx/CVE-2026-83612.json
- https://github.com/xmldom/xmldom/security/advisories/GHSA-6mj3-qw4j-hgrw
- https://nvd.nist.gov/vuln/detail/CVE-2026-83612
- https://github.com/xmldom/xmldom/commit/7ced40c06c28d151e996a97045018c3559ae4707
- https://github.com/xmldom/xmldom/pull/1071
