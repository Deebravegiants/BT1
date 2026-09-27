# [H] CVE-2025-57106

## Summary
Severity: High
Advisory: CVE-2025-57106
Aliases: PYSEC-2025-224
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-31
Source: https://osv.dev/vulnerability/CVE-2025-57106
Type: osv

## Details
Kitware VTK (Visualization Toolkit) up to 9.5.0 is vulnerable to Buffer Overflow in vtkGLTFDocumentLoader. The vulnerability occurs in the BufferDataExtractionWorker template function when processing GLTF accessor data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57106.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57106
- https://gitlab.kitware.com/vtk/vtk/-/issues/19733
- https://gitlab.kitware.com/vtk/vtk/-/issues/19734
