# [H] ALPINE-CVE-2019-11471

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-11471
Ecosystem: Alpine:v3.11, Alpine:v3.23
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-04-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-11471
Type: osv

## Affected
- Alpine:v3.11: `libheif` — affected >=0 <1.5.0-r0
- Alpine:v3.23: `libheif` — affected >=0 <1.5.0-r0

## Details
libheif 1.4.0 has a use-after-free in heif::HeifContext::Image::set_alpha_channel in heif_context.h because heif_context.cc mishandles references to non-existing alpha images.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-11471
