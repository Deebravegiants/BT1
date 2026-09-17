# [M] xmldom: Quadratic-time parsing via the malformed-input recovery path — `parseElementStartPart` re-scan and `normalize()` adjacent-text merge

## Summary
Severity: Medium
Advisory: CVE-2026-83614
Aliases: GHSA-93r5-fhx6-vmg9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-83614
Type: osv

## Details
xmldom is a pure JavaScript W3C standard-based (XML DOM Level 2 Core) DOMParser and XMLSerializer module. Prior to @xmldom/xmldom versions 0.8.15 and 0.9.12, and in xmldom versions 0.3.0 through 0.6.0, two independent quadratic paths can cause denial of service. In lib/sax.js, parseElementStartPart repeatedly rescans a malformed tag name to the next > during single-character recovery; in lib/dom.js, normalize() repeatedly removes and appends adjacent text nodes, causing quadratic reindexing and string rebuilding. The first path is reachable through default DOMParser.parseFromString() processing, while the second is also reachable through a direct normalize() call on a programmatically constructed DOM, and endDocument invokes that normalization after parsing. This issue is fixed in @xmldom/xmldom versions 0.8.15 and 0.9.12; no fixed version is available for xmldom.

## References
- https://github.com/xmldom/xmldom/releases/tag/0.8.15
- https://github.com/xmldom/xmldom/releases/tag/0.9.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/83xxx/CVE-2026-83614.json
- https://github.com/xmldom/xmldom/security/advisories/GHSA-93r5-fhx6-vmg9
- https://nvd.nist.gov/vuln/detail/CVE-2026-83614
- https://github.com/xmldom/xmldom/commit/0748720b620555f8c222782dcab575cf0cf403b4
- https://github.com/xmldom/xmldom/commit/f40ccb861eee0acbf5ee4feb9a34932e87b329c9
- https://github.com/xmldom/xmldom/pull/1071
- https://github.com/xmldom/xmldom/pull/1072
