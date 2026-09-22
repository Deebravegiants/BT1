# [M] CVE-2018-19876

## Summary
Severity: Medium
Advisory: CVE-2018-19876
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-05
Source: https://osv.dev/vulnerability/CVE-2018-19876
Type: osv

## Details
cairo 1.16.0, in cairo_ft_apply_variations() in cairo-ft-font.c, would free memory using a free function incompatible with WebKit's fastMalloc, leading to an application crash with a "free(): invalid pointer" error.

## References
- https://gitlab.freedesktop.org/cairo/cairo/merge_requests/5
- https://bugs.webkit.org/show_bug.cgi?id=191595
