# [M] A vulnerability was determined in LibTIFF up to 4.5.1

## Summary
Severity: Medium
Advisory: JLSEC-2025-321
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-321
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.6.0+0

## Details
A vulnerability was determined in LibTIFF up to 4.5.1. Affected by this issue is the function readSeparateStripsetoBuffer of the file `tools/tiffcrop.c` of the component tiffcrop. The manipulation leads to stack-based buffer overflow. Local access is required to approach this attack. The patch is identified as 8a7a48d7a645992ca83062b3a1873c951661e2b3. It is recommended to apply a patch to fix this issue.

## References
- http://www.libtiff.org/
- https://gitlab.com/libtiff/libtiff/-/commit/8a7a48d7a645992ca83062b3a1873c951661e2b3
- https://vuldb.com/?ctiid.319382
- https://vuldb.com/?id.319382
- https://vuldb.com/?submit.624604
