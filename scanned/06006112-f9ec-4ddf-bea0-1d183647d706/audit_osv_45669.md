# [M] JLSEC-2026-186

## Summary
Severity: Medium
Advisory: JLSEC-2026-186
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-186
Type: osv

## Affected
- Julia: `assimp_jll` — affected >=5.2.5+0 <6.0.4+0

## Details
Open Asset Import Library (assimp) commit 3c253ca was discovered to contain a segmentation violation via the component Assimp::XFileImporter::CreateMeshes.

## References
- https://github.com/assimp/assimp/issues/4662
