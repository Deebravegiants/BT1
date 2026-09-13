# [M] CVE-2026-42478

## Summary
Severity: Medium
Advisory: CVE-2026-42478
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-42478
Type: osv

## Details
An issue was discovered in VrmlData_IndexedFaceSet::TShape in the VRML V2.0 parser in Open CASCADE Technology (OCCT) V8_0_0_rc5 allows attackers to cause a denial of service via a crafted VRML file. The issue occurs because malformed VRML input can trigger dereference of a corrupt or unvalidated pointer during shape construction in libTKDEVRML.so.

## References
- https://gist.github.com/sgInnora/dfba083d04906283e9c92aea78e2d94a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42478.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42478
