# [M] CVE-2021-21366

## Summary
Severity: Medium
Advisory: CVE-2021-21366
Aliases: GHSA-h6q6-9hqw-rwfv
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2021-03-12
Source: https://osv.dev/vulnerability/CVE-2021-21366
Type: osv

## Details
xmldom is a pure JavaScript W3C standard-based (XML DOM Level 2 Core) DOMParser and XMLSerializer module. xmldom versions 0.4.0 and older do not correctly preserve system identifiers, FPIs or namespaces when repeatedly parsing and serializing maliciously crafted documents. This may lead to unexpected syntactic changes during XML processing in some downstream applications. This is fixed in version 0.5.0. As a workaround downstream applications can validate the input and reject the maliciously crafted documents.

## References
- https://www.npmjs.com/package/xmldom
- https://github.com/xmldom/xmldom/releases/tag/0.5.0
- https://github.com/xmldom/xmldom/security/advisories/GHSA-h6q6-9hqw-rwfv
- https://lists.debian.org/debian-lts-announce/2023/01/msg00000.html
- https://github.com/xmldom/xmldom/commit/d4201b9dfbf760049f457f9f08a3888d48835135
