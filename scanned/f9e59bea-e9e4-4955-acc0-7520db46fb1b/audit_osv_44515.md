# [M] xmldom: Attribute name injection via setAttribute() bypasses requireWellFormed

## Summary
Severity: Medium
Advisory: CVE-2026-83605
Aliases: GHSA-4w3w-2rp5-g8jm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-83605
Type: osv

## Details
xmldom is a pure JavaScript W3C standard-based (XML DOM Level 2 Core) DOMParser and XMLSerializer module. Prior to @xmldom/xmldom versions 0.8.14 and 0.9.11, and in xmldom version 0.6.0 and earlier, Element.setAttribute() calls the private _createAttribute(name) path without validating the attribute name, while Document.createAttribute(name) validates against QName. XMLSerializer.serializeToString() emits attribute names verbatim, and requireWellFormed: true did not validate them, so a crafted name can terminate the intended attribute and inject additional attributes, including event handlers, into browser-consumed output; synthesized xmlns:PREFIX declarations expose the same unchecked-name boundary. This issue is fixed in @xmldom/xmldom versions 0.8.14 and 0.9.11; no fixed version is available for xmldom.

## References
- https://github.com/xmldom/xmldom/releases/tag/0.8.14
- https://github.com/xmldom/xmldom/releases/tag/0.9.11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/83xxx/CVE-2026-83605.json
- https://github.com/xmldom/xmldom/security/advisories/GHSA-4w3w-2rp5-g8jm
- https://nvd.nist.gov/vuln/detail/CVE-2026-83605
- https://github.com/xmldom/xmldom/commit/cba1321218b069182695813fa7565653708e172e
- https://github.com/xmldom/xmldom/commit/d8212e632507eaf1d9f609657dd4c56abeb12d44
- https://github.com/xmldom/xmldom/pull/1043
- https://github.com/xmldom/xmldom/pull/1050
