# [M] FreeCAD: XXE file read and SSRF via external entity injection in Document.xml SAX parser

## Summary
Severity: Medium
Advisory: CVE-2026-73235
Aliases: GHSA-cp6c-87x9-xf49
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73235
Type: osv

## Details
FreeCAD is a free and open-source multiplatform 3D parametric modeler. Prior to 1.1.2, the Xerces SAX2 XMLReader constructed in src/Base/Reader.cpp by Base::XMLReader::XMLReader() parses attacker-controlled Document.xml from a crafted .FCStd archive without disabling default external entity resolution or external DTD loading. When Document::restore() opens the document, external entities can read local files through the file URI scheme or initiate server-side requests through the http URI scheme, and resolved content can flow through the characters() callback. This issue is fixed in version 1.1.2.

## References
- https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73235.json
- https://github.com/FreeCAD/FreeCAD/security/advisories/GHSA-cp6c-87x9-xf49
- https://nvd.nist.gov/vuln/detail/CVE-2026-73235
- https://github.com/FreeCAD/FreeCAD/commit/7d1b8f5806db578db99feb348e55a6b0eaff7c73
- https://github.com/FreeCAD/FreeCAD/commit/d98eaf1f194400d8a8886fe6780c54f5c68ea2c3
- https://github.com/FreeCAD/FreeCAD/pull/31271
- https://github.com/FreeCAD/FreeCAD/pull/31280
