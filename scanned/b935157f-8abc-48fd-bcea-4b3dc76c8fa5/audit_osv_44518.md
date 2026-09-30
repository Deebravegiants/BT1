# [M] xmldom: DocType `name` Injection Bypasses requireWellFormed

## Summary
Severity: Medium
Advisory: CVE-2026-83608
Aliases: GHSA-27p8-2357-5qqv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-83608
Type: osv

## Details
xmldom is a pure JavaScript W3C standard-based (XML DOM Level 2 Core) DOMParser and XMLSerializer module. Prior to @xmldom/xmldom versions 0.8.15 and 0.9.12, and in xmldom version 0.6.0 and earlier, the DOCUMENT_TYPE_NODE branch in lib/dom.js validates publicId, systemId, and internalSubset under requireWellFormed: true but emits DocumentType.name verbatim. A name containing > or whitespace can terminate the <!DOCTYPE ...> declaration and inject sibling markup; the value can be supplied through createDocumentType() on the 0.8.x and unscoped lines or through a direct DocumentType.name property write on every affected line. The default path and legacy creation-time behavior remain permissive, while the vulnerable strict path fails to enforce an XML Name. This issue is fixed in @xmldom/xmldom versions 0.8.15 and 0.9.12; no fixed version is available for xmldom.

## References
- https://github.com/xmldom/xmldom/releases/tag/0.8.15
- https://github.com/xmldom/xmldom/releases/tag/0.9.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/83xxx/CVE-2026-83608.json
- https://github.com/xmldom/xmldom/security/advisories/GHSA-27p8-2357-5qqv
- https://nvd.nist.gov/vuln/detail/CVE-2026-83608
- https://github.com/xmldom/xmldom/commit/57aec90ac57b4408ae7c5d1746bf2a693b5ed90e
- https://github.com/xmldom/xmldom/commit/85f12eb4d14b44de33216cfb72b50af4d24e9fdd
- https://github.com/xmldom/xmldom/pull/1071
- https://github.com/xmldom/xmldom/pull/1072
