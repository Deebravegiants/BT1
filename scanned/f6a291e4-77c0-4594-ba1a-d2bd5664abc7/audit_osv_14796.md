# [H] CVE-2019-11471

## Summary
Severity: High
Advisory: CVE-2019-11471
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-04-23
Source: https://osv.dev/vulnerability/CVE-2019-11471
Type: osv

## Details
libheif 1.4.0 has a use-after-free in heif::HeifContext::Image::set_alpha_channel in heif_context.h because heif_context.cc mishandles references to non-existing alpha images.

## References
- https://github.com/strukturag/libheif/commit/995a4283d8ed2d0d2c1ceb1a577b993df2f0e014
- https://github.com/strukturag/libheif/issues/123
