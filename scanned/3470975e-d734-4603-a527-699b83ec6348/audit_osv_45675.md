# [H] JLSEC-2026-192

## Summary
Severity: High
Advisory: JLSEC-2026-192
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-192
Type: osv

## Affected
- Julia: `assimp_jll` — affected >=0 <6.0.4+0

## Details
A vulnerability was found in Open Asset Import Library Assimp 5.4.3. It has been classified as problematic. Affected is the function LWOImporter::CountVertsAndFacesLWO2 of the file `assimp/code/AssetLib/LWO/LWOLoader.cpp`. The manipulation leads to out-of-bounds read. The attack needs to be approached locally. The exploit has been disclosed to the public and may be used. The project decided to collect all Fuzzer bugs in a main-issue to address them in the future.

## References
- https://github.com/assimp/assimp/issues/6128
- https://github.com/assimp/assimp/issues/6173
- https://github.com/assimp/assimp/issues/6174
- https://github.com/user-attachments/files/20209125/line-832-reproducer.zip
- https://vuldb.com/?ctiid.310290
- https://vuldb.com/?id.310290
- https://vuldb.com/?submit.578006
