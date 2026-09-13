# [C] CVE-2025-57108

## Summary
Severity: Critical
Advisory: CVE-2025-57108
Aliases: PYSEC-2025-226
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-31
Source: https://osv.dev/vulnerability/CVE-2025-57108
Type: osv

## Details
Kitware VTK (Visualization Toolkit) through 9.5.0 contains a heap use-after-free vulnerability in vtkGLTFDocumentLoader. The vulnerability manifests during mesh object copy operations where vector members are accessed after the underlying memory has been freed, specifically when handling GLTF files with corrupted or invalid mesh reference structures.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57108.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57108
- https://gitlab.kitware.com/vtk/vtk/-/issues/19736
