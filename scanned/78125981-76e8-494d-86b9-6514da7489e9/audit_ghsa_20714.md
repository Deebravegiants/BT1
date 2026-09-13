# [H] VTK NULL pointer dereference vulnerability

## Summary
Severity: High
Advisory: GHSA-xfhg-9pjg-xg7g
CVE: CVE-2021-42521
CWE: CWE-400, CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-26
Source: https://github.com/advisories/GHSA-xfhg-9pjg-xg7g
Type: github-advisory

## Affected
- PyPI: `vtk` — affected >=0 <9.0.1

## Details
There is a NULL pointer dereference vulnerability in VTK, and it lies in IO/Infovis/vtkXMLTreeReader.cxx. The vendor didn't check the return value of libxml2 API 'xmlDocGetRootElement', and try to dereference it. It is unsafe as the return value can be NULL and that NULL pointer dereference may crash the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42521
- https://discourse.vtk.org/t/vtk-9-2-5-is-out/10549
- https://github.com/pypa/advisory-database/tree/main/vulns/vtk/PYSEC-2022-255.yaml
- https://gitlab.kitware.com/vtk/vtk
- https://gitlab.kitware.com/vtk/vtk/issues/17818
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PCTMSAAVP4BW2HTZLDWMGKZ2WEC5OFLK
