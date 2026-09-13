# [H] FreeCAD: Arbitrary code execution via unsandboxed PyImport_ImportModule in PropertyPythonObject::Restore

## Summary
Severity: High
Advisory: CVE-2026-34789
Aliases: GHSA-493w-pp4h-h77v
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-34789
Type: osv

## Details
FreeCAD is a free and open-source multiplatform 3D parametric modeler. Prior to 1.1.2, src/App/PropertyPythonObject.cpp in PropertyPythonObject::Restore() passes the attacker-controlled module attribute from serialized PropertyPythonObject XML directly to PyImport_ImportModule() while restoring a crafted FCStd document, which executes module-level Python code, and the legacy pickle branch also imports an attacker-controlled module and invokes its class constructor through PyObject_CallObject(). This issue is fixed in version 1.1.2.

## References
- https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34789.json
- https://github.com/FreeCAD/FreeCAD/security/advisories/GHSA-493w-pp4h-h77v
- https://nvd.nist.gov/vuln/detail/CVE-2026-34789
- https://github.com/FreeCAD/FreeCAD/commit/81b73925ce22610542367301d8eff4259eb9596e
- https://github.com/FreeCAD/FreeCAD/commit/983037f3003dc31f48db36705b86fb3fbe026295
- https://github.com/FreeCAD/FreeCAD/commit/e2dc6c8172673642c6856b8b3a5a6accefb18279
