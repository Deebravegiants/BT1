# [M] CVE-2025-57109

## Summary
Severity: Medium
Advisory: CVE-2025-57109
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2025-10-30
Source: https://osv.dev/vulnerability/CVE-2025-57109
Type: osv

## Details
Kitware VTK (Visualization Toolkit) 9.5.0 is vulnerable to Heap Use-After-Free in vtkGLTFImporter::ImportActors. When processing GLTF files with invalid scene node references, the application accesses string members of mesh objects that have been previously freed during actor import operations.

## References
- https://gitlab.kitware.com/vtk/vtk/-/issues/19735
