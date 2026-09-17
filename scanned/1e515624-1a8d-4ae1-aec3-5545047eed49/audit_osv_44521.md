# [M] xmldom: Quadratic-time attribute deduplication

## Summary
Severity: Medium
Advisory: CVE-2026-83613
Aliases: GHSA-8344-3jmq-59r6
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-83613
Type: osv

## Details
xmldom is a pure JavaScript W3C standard-based (XML DOM Level 2 Core) DOMParser and XMLSerializer module. Prior to @xmldom/xmldom versions 0.8.15 and 0.9.12, and in xmldom version 0.6.0 and earlier, DOMHandler.startElement in lib/dom-parser.js inserts every parsed attribute through setAttributeNode, while NamedNodeMap.setNamedItem in lib/dom.js calls the linear getNamedItem or getNamedItemNS lookup for each insertion. A well-formed element with many distinct attributes therefore requires quadratic comparisons during DOMParser.parseFromString() and can stall a Node.js event loop before application validation. This issue is fixed in @xmldom/xmldom versions 0.8.15 and 0.9.12; no fixed version is available for xmldom.

## References
- https://github.com/xmldom/xmldom/releases/tag/0.8.15
- https://github.com/xmldom/xmldom/releases/tag/0.9.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/83xxx/CVE-2026-83613.json
- https://github.com/xmldom/xmldom/security/advisories/GHSA-8344-3jmq-59r6
- https://nvd.nist.gov/vuln/detail/CVE-2026-83613
- https://github.com/xmldom/xmldom/commit/2c548f200cfec991cd5846627ef8f03542309213
- https://github.com/xmldom/xmldom/commit/cfb09b5dbeb035fdfedc9f01e2bbaf226bf47cf3
- https://github.com/xmldom/xmldom/pull/1071
- https://github.com/xmldom/xmldom/pull/1072
- https://github.com/xmldom/xmldom/security/advisories/GHSA-27p8-2357-5qqv
