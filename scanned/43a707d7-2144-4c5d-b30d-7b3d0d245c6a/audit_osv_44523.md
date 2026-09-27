# [M] xmldom: Quadratic-memory consumption

## Summary
Severity: Medium
Advisory: CVE-2026-83615
Aliases: GHSA-965w-775f-mr7g
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-83615
Type: osv

## Details
xmldom is a pure JavaScript W3C standard-based (XML DOM Level 2 Core) DOMParser and XMLSerializer module. Prior to @xmldom/xmldom versions 0.8.15 and 0.9.12, and in xmldom versions 0.1.5 through 0.6.0, appendElement in lib/sax.js uses _copy to clone the complete currentNSMap for each nested element that declares a new namespace prefix. Keeping every ancestor map live on the parse stack creates quadratic peak namespace-map storage, so a small highly compressible XML document can exhaust the process heap before application validation. This issue is fixed in @xmldom/xmldom versions 0.8.15 and 0.9.12; no fixed version is available for xmldom.

## References
- https://github.com/xmldom/xmldom/releases/tag/0.8.15
- https://github.com/xmldom/xmldom/releases/tag/0.9.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/83xxx/CVE-2026-83615.json
- https://github.com/xmldom/xmldom/security/advisories/GHSA-965w-775f-mr7g
- https://nvd.nist.gov/vuln/detail/CVE-2026-83615
- https://github.com/xmldom/xmldom/commit/954370f58c046223faf95ba77efcbc8ce014409d
- https://github.com/xmldom/xmldom/commit/dabffe884e864eeecb1f515c716f875e1bc47ec1
- https://github.com/xmldom/xmldom/pull/1071
- https://github.com/xmldom/xmldom/pull/1072
