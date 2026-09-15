# [H] CVE-2025-57107

## Summary
Severity: High
Advisory: CVE-2025-57107
Aliases: PYSEC-2025-225
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2025-10-31
Source: https://osv.dev/vulnerability/CVE-2025-57107
Type: osv

## Details
Kitware VTK (Visualization Toolkit) through 9.5.0 contains a heap buffer overflow vulnerability in vtkGLTFDocumentLoader. When processing specially crafted GLTF files, the copy constructor of Accessor objects fails to properly validate buffer boundaries before performing memory read operations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57107.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57107
- https://gitlab.kitware.com/vtk/vtk/-/issues/19732
