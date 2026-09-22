# [H] FreeCAD: FCStd path traversal allows arbitrary file write via unsanitized file attribute in PropertyFileIncluded::Restore()

## Summary
Severity: High
Advisory: CVE-2026-73234
Aliases: GHSA-5vqh-3v38-jw2r
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73234
Type: osv

## Details
FreeCAD is a free and open-source multiplatform 3D parametric modeler. Prior to 1.1.2, PropertyFileIncluded::Restore() in src/App/PropertyFile.cpp concatenates an attacker-controlled file or data attribute from Document.xml with the document transient path without rejecting directory components, absolute paths, or parent traversal. A crafted .FCStd archive with a matching FileIncluded XML attribute and ZIP entry can therefore write attacker-controlled content to arbitrary locations accessible to the FreeCAD user, potentially enabling persistence, credential compromise, configuration replacement, or code execution. This issue is fixed in version 1.1.2.

## References
- https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73234.json
- https://github.com/FreeCAD/FreeCAD/security/advisories/GHSA-5vqh-3v38-jw2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-73234
- https://github.com/FreeCAD/FreeCAD/commit/7cabda0979779251bad516cb6911a43dc03c5203
- https://github.com/FreeCAD/FreeCAD/commit/f19b18b7d93729a29a90e96e0ae192b5d054b86d
- https://github.com/FreeCAD/FreeCAD/pull/31269
- https://github.com/FreeCAD/FreeCAD/pull/31281
