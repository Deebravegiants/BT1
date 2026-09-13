# [H] JLSEC-2026-195

## Summary
Severity: High
Advisory: JLSEC-2026-195
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-195
Type: osv

## Affected
- Julia: `assimp_jll` — affected >=0 <6.0.4+0

## Details
A vulnerability classified as problematic has been found in Open Asset Import Library Assimp 5.4.3. This affects the function `MDLImporter::ParseSkinLump_3DGS_MDL7` of the file `assimp/code/AssetLib/MDL/MDLMaterialLoader.cpp`. The manipulation leads to out-of-bounds read. Attacking locally is a requirement. The exploit has been disclosed to the public and may be used. The project decided to collect all Fuzzer bugs in a main-issue to address them in the future.

## References
- https://github.com/assimp/assimp/issues/6128
- https://github.com/assimp/assimp/issues/6176
- https://github.com/user-attachments/files/20209911/ParseSkinLump-reproducer.zip
- https://vuldb.com/?ctiid.310293
- https://vuldb.com/?id.310293
- https://vuldb.com/?submit.578013
