# [H] A vulnerability was found in LibTIFF up to 4.7.0

## Summary
Severity: High
Advisory: JLSEC-2025-318
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-318
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.7.2+0

## Details
A vulnerability was found in LibTIFF up to 4.7.0. It has been rated as critical. This issue affects the function setrow of the file `tools/thumbnail.c`. The manipulation leads to buffer overflow. An attack has to be approached locally. The patch is named e8c9d6c616b19438695fd829e58ae4fde5bfbc22. It is recommended to apply a patch to fix this issue. This vulnerability only affects products that are no longer supported by the maintainer.

## References
- http://www.libtiff.org/
- https://gitlab.com/libtiff/libtiff/-/commit/e8c9d6c616b19438695fd829e58ae4fde5bfbc22
- https://gitlab.com/libtiff/libtiff/-/issues/715
- https://gitlab.com/libtiff/libtiff/-/merge_requests/737
- https://vuldb.com/?ctiid.317591
- https://vuldb.com/?id.317591
- https://vuldb.com/?submit.621797
