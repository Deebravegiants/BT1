# [H] FreeCAD: Arbitrary Code Execution via eval() on untrusted SVG template scale field in BIM TechDraw Page

## Summary
Severity: High
Advisory: CVE-2026-34399
Aliases: GHSA-chv4-vm6r-wjqj
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-34399
Type: osv

## Details
FreeCAD is a free and open-source multiplatform 3D parametric modeler. From 0.19 until 1.1.1, FreeCAD's BIM Workbench contains an eval() call on untrusted data from SVG template files. When a user creates a TechDraw page from a malicious SVG template, arbitrary Python code executes. The vulnerable code is in src/Mod/BIM/bimcommands/BimTDPage.py (line 87). This issue is fixed in version 1.1.1.

## References
- https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34399.json
- https://github.com/FreeCAD/FreeCAD/security/advisories/GHSA-chv4-vm6r-wjqj
- https://nvd.nist.gov/vuln/detail/CVE-2026-34399
