# [M] CVE-2026-42481

## Summary
Severity: Medium
Advisory: CVE-2026-42481
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-42481
Type: osv

## Details
Open CASCADE Technology (OCCT) V8_0_0_rc5 contains multiple vulnerabilities in its IGES and STEP file parsers that can be triggered by crafted IGES or STEP files. These issues include an out-of-bounds read in Geom2d_BSplineCurve::EvalD0 during IGES B-spline curve evaluation, an out-of-bounds read in MakeBSplineCurveCommon during STEP B-spline curve construction, and infinite recursion in StepShape_OrientedEdge::EdgeStart when processing a self-referential OrientedEdge entity. Successful exploitation may result in denial of service or unintended memory disclosure.

## References
- https://gist.github.com/sgInnora/dfba083d04906283e9c92aea78e2d94a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42481.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42481
