# [H] JLSEC-2026-189

## Summary
Severity: High
Advisory: JLSEC-2026-189
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-189
Type: osv

## Affected
- Julia: `assimp_jll` — affected >=0 <6.0.4+0

## Details
A security vulnerability has been detected in Open Asset Import Library Assimp up to 6.0.2. Affected by this vulnerability is the function Assimp::LWOImporter::FindUVChannels of the file `/src/assimp/code/AssetLib/LWO/LWOMaterial.cpp`. Such manipulation leads to use after free. The attack needs to be performed locally. The exploit has been disclosed publicly and may be used. This and similar defects are tracked and handled via issue #6128.

## References
- https://github.com/assimp/assimp/issues/6258
- https://github.com/assimp/assimp/issues/6258#issuecomment-3070999530
- https://github.com/user-attachments/files/21216542/assimp_poc10.zip
- https://vuldb.com/?ctiid.341727
- https://vuldb.com/?id.341727
- https://vuldb.com/?submit.735232
