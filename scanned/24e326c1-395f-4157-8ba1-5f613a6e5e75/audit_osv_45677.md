# [H] JLSEC-2026-194

## Summary
Severity: High
Advisory: JLSEC-2026-194
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-194
Type: osv

## Affected
- Julia: `assimp_jll` — affected >=0 <6.0.4+0

## Details
A vulnerability was found in Open Asset Import Library Assimp 5.4.3. It has been rated as problematic. Affected by this issue is the function SkipSpaces in the library `assimp/include/assimp/ParsingUtils.h`. The manipulation leads to out-of-bounds read. Local access is required to approach this attack. The exploit has been disclosed to the public and may be used. The project decided to collect all Fuzzer bugs in a main-issue to address them in the future.

## References
- https://github.com/assimp/assimp/issues/6128
- https://github.com/assimp/assimp/issues/6175
- https://github.com/user-attachments/files/20209469/reproducer.zip
- https://vuldb.com/?ctiid.310292
- https://vuldb.com/?id.310292
- https://vuldb.com/?submit.578012
