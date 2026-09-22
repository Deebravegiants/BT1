# [H] FreeCAD: Arbitrary Code Execution via eval() on untrusted project file metadata in BIM Workbench

## Summary
Severity: High
Advisory: CVE-2026-34398
Aliases: GHSA-8rfj-7956-6gwf
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-34398
Type: osv

## Details
FreeCAD is a free and open-source multiplatform 3D parametric modeler. From 0.19 until 1.1.1, src/Mod/BIM/bimcommands/BimProjectManager.py in the BIM Project Manager Load Template flow passes attacker-controlled FCStd Meta property values for wpposition, wpu, wpv, and wpaxis directly to eval(), allowing arbitrary Python code execution when a user loads a malicious BIM project template. This issue is fixed in version 1.1.1.

## References
- https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34398.json
- https://github.com/FreeCAD/FreeCAD/security/advisories/GHSA-8rfj-7956-6gwf
- https://nvd.nist.gov/vuln/detail/CVE-2026-34398
- https://github.com/FreeCAD/FreeCAD/commit/871ee19b76224910332bbfbd39eebbede967998b
- https://github.com/FreeCAD/FreeCAD/commit/9ed351cc4700db0a94c46f020c34c58bbf1bdaba
- https://github.com/FreeCAD/FreeCAD/pull/28610
