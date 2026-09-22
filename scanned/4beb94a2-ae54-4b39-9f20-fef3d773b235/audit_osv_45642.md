# [M] JLSEC-2026-157

## Summary
Severity: Medium
Advisory: JLSEC-2026-157
Ecosystem: Julia
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/JLSEC-2026-157
Type: osv

## Affected
- Julia: `libde265_jll` — affected >=0 <1.0.18000+0

## Details
strukturag libde265 commit d9fea9d wa discovered to contain a segmentation fault via the component `decoder_context::compute_framedrop_table()`.

## References
- https://gist.github.com/optionGo/e6567a1c2bc4e0c9fee4e1e8be8d6af9
- https://github.com/strukturag/libde265/commit/8b17e0930f77db07f55e0b89399a8f054ddbecf7
- https://github.com/strukturag/libde265/issues/484
