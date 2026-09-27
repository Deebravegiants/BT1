# [M] xmldom: Processing Instruction Target Injection Bypasses requireWellFormed

## Summary
Severity: Medium
Advisory: CVE-2026-83616
Aliases: GHSA-c7q8-3ch8-vqpv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-83616
Type: osv

## Details
xmldom is a pure JavaScript W3C standard-based (XML DOM Level 2 Core) DOMParser and XMLSerializer module. Prior to @xmldom/xmldom versions 0.8.15 and 0.9.12, and in xmldom version 0.6.0 and earlier, Document.createProcessingInstruction(target, data) in lib/dom.js accepts an unvalidated target, while the requireWellFormed: true serializer checks only for a colon and the reserved case-insensitive xml name on 0.9.x and performs no target check on 0.8.x. Because serialization emits <?target data?>, a target containing >, ?, whitespace, or another invalid XML-name character can break the processing-instruction boundary and inject XML structure. This issue is fixed in @xmldom/xmldom versions 0.8.15 and 0.9.12; no fixed version is available for xmldom.

## References
- https://github.com/xmldom/xmldom/releases/tag/0.8.15
- https://github.com/xmldom/xmldom/releases/tag/0.9.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/83xxx/CVE-2026-83616.json
- https://github.com/xmldom/xmldom/security/advisories/GHSA-c7q8-3ch8-vqpv
- https://nvd.nist.gov/vuln/detail/CVE-2026-83616
- https://github.com/xmldom/xmldom/commit/1cde3e31a07c41c87cfd368d6946aa477f16b4f9
- https://github.com/xmldom/xmldom/commit/3b694872bcb5c7e3cbadba961a4be2488750ce5b
- https://github.com/xmldom/xmldom/pull/1071
- https://github.com/xmldom/xmldom/pull/1072
