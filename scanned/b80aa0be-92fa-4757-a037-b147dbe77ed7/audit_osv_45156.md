# [M] cairo 1.16.0, in `cairo_ft_apply_variations()` in cairo-ft-font.c, would free memory using a free...

## Summary
Severity: Medium
Advisory: JLSEC-2025-14
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-10-10
Source: https://osv.dev/vulnerability/JLSEC-2025-14
Type: osv

## Affected
- Julia: `Cairo_jll` — affected >=1.16.0+0 <1.18.0+0

## Details
cairo 1.16.0, in `cairo_ft_apply_variations()` in cairo-ft-font.c, would free memory using a free function incompatible with WebKit's fastMalloc, leading to an application crash with a "free(): invalid pointer" error.

## References
- https://bugs.webkit.org/show_bug.cgi?id=191595
- https://gitlab.freedesktop.org/cairo/cairo/merge_requests/5
