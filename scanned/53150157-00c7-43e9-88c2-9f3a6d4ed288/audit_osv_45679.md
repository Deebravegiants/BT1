# [M] JLSEC-2026-196

## Summary
Severity: Medium
Advisory: JLSEC-2026-196
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-196
Type: osv

## Affected
- Julia: `assimp_jll` — affected >=0 <6.0.4+0

## Details
A vulnerability classified as critical has been found in Open Asset Import Library Assimp up to 5.4.3. Affected is the function Assimp::BVHLoader::ReadNodeChannels in the library `assimp/code/AssetLib/BVH/BVHLoader.cpp`. The manipulation of the argument pNode leads to use after free. Attacking locally is a requirement. The exploit has been disclosed to the public and may be used. The project decided to collect all Fuzzer bugs in a main-issue to address them in the future.

## References
- https://github.com/assimp/assimp/issues/6219
- https://github.com/assimp/assimp/issues/6219#issuecomment-2945016005
- https://github.com/user-attachments/files/20604791/reproduce_2.tar.gz
- https://vuldb.com/?ctiid.312588
- https://vuldb.com/?id.312588
- https://vuldb.com/?submit.591233
