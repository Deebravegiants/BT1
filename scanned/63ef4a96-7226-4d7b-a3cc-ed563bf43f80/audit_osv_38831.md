# [M] CVE-2026-42480

## Summary
Severity: Medium
Advisory: CVE-2026-42480
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-42480
Type: osv

## Details
A stack-based out-of-bounds read vulnerability in VrmlData_Scene::ReadLine in the VRML parser in Open CASCADE Technology (OCCT) V8_0_0_rc5 allows attackers to cause a denial of service via a crafted VRML file. The issue occurs because the quoted-string escape handler uses ptr[++anOffset] without proper bounds checking, which can read past the end of a fixed-size stack buffer.

## References
- https://gist.github.com/sgInnora/dfba083d04906283e9c92aea78e2d94a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42480.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42480
