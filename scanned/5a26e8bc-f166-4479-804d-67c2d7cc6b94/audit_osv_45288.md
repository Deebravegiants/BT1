# [H] A vulnerability was found in LibTIFF up to 4.7.0

## Summary
Severity: High
Advisory: JLSEC-2025-317
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-317
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.7.2+0

## Details
A vulnerability was found in LibTIFF up to 4.7.0. It has been declared as critical. This vulnerability affects the function `get_histogram` of the file `tools/tiffmedian.c`. The manipulation leads to use after free. The attack needs to be approached locally. The exploit has been disclosed to the public and may be used. The patch is identified as fe10872e53efba9cc36c66ac4ab3b41a839d5172. It is recommended to apply a patch to fix this issue.

## References
- http://www.libtiff.org/
- https://gitlab.com/libtiff/libtiff/-/commit/fe10872e53efba9cc36c66ac4ab3b41a839d5172
- https://gitlab.com/libtiff/libtiff/-/issues/707
- https://gitlab.com/libtiff/libtiff/-/merge_requests/727
- https://vuldb.com/?ctiid.317590
- https://vuldb.com/?id.317590
- https://vuldb.com/?submit.621796
