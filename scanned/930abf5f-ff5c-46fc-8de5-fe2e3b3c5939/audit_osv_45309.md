# [C] An out-of-bounds read flaw was found in the CLARRV, DLARRV, SLARRV, and ZLARRV functions in lapack...

## Summary
Severity: Critical
Advisory: JLSEC-2025-6
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-10-08
Source: https://osv.dev/vulnerability/JLSEC-2025-6
Type: osv

## Affected
- Julia: `LAPACK32_jll` — affected >=0 <3.10.1+0
- Julia: `LAPACK_jll` — affected >=0 <3.10.1+0
- Julia: `MadNLP` — affected >=0 <0.2.0
- Julia: `MadNLPHSL` — affected >=0 <0.4.0
- Julia: `MadNLPPardiso` — affected unspecified
- Julia: `OpenBLAS32_jll` — affected >=0 <0.3.20+0
- Julia: `OpenBLASHighCoreCount_jll` — affected unspecified
- Julia: `OpenBLAS_jll` — affected >=0 <0.3.20+0
- Julia: `libjulia_jll` — affected >=0 <1.8.0+1

## Details
An out-of-bounds read flaw was found in the CLARRV, DLARRV, SLARRV, and ZLARRV functions in lapack through version 3.10.0, as also used in OpenBLAS before version 0.3.18. Specially crafted inputs passed to these functions could cause an application using lapack to crash or possibly disclose portions of its memory.

## References
- https://github.com/JuliaLang/julia/issues/42415
- https://github.com/Reference-LAPACK/lapack/commit/38f3eeee3108b18158409ca2a100e6fe03754781
- https://github.com/Reference-LAPACK/lapack/pull/625
- https://github.com/xianyi/OpenBLAS/commit/2be5ee3cca97a597f2ee2118808a2d5eacea050c
- https://github.com/xianyi/OpenBLAS/commit/337b65133df174796794871b3988cd03426e6d41
- https://github.com/xianyi/OpenBLAS/commit/ddb0ff5353637bb5f5ad060c9620e334c143e3d7
- https://github.com/xianyi/OpenBLAS/commit/fe497efa0510466fd93578aaf9da1ad8ed4edbe7
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6QFEVOCUG2UXMVMFMTU4ONJVDEHY2LW2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DROZM4M2QRKSD6FBO4BHSV2QMIRJQPHT/
