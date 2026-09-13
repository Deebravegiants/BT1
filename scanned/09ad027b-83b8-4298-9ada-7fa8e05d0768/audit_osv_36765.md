# [M] LIBPNG has a heap buffer overflow in png_set_quantize

## Summary
Severity: Medium
Advisory: CVE-2026-25646
Aliases: GHSA-g8hp-mq4h-rqm3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-10
Source: https://osv.dev/vulnerability/CVE-2026-25646
Type: osv

## Details
LIBPNG is a reference library for use in applications that read, create, and manipulate PNG (Portable Network Graphics) raster image files. Prior to 1.6.55, an out-of-bounds read vulnerability exists in the png_set_quantize() API function. When the function is called with no histogram and the number of colors in the palette is more than twice the maximum supported by the user's display, certain palettes will cause the function to enter into an infinite loop that reads past the end of an internal heap-allocated buffer. The images that trigger this vulnerability are valid per the PNG specification. This vulnerability is fixed in 1.6.55.

## References
- http://www.openwall.com/lists/oss-security/2026/02/09/7
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-25646.json
- https://access.redhat.com/errata/RHSA-2026:10097
- https://access.redhat.com/errata/RHSA-2026:12274
- https://access.redhat.com/errata/RHSA-2026:14773
- https://access.redhat.com/errata/RHSA-2026:15087
- https://access.redhat.com/errata/RHSA-2026:16174
- https://access.redhat.com/errata/RHSA-2026:17596
- https://access.redhat.com/errata/RHSA-2026:3031
- https://access.redhat.com/errata/RHSA-2026:3405
- https://access.redhat.com/errata/RHSA-2026:3551
- https://access.redhat.com/errata/RHSA-2026:3573
- https://access.redhat.com/errata/RHSA-2026:3574
- https://access.redhat.com/errata/RHSA-2026:3575
- https://access.redhat.com/errata/RHSA-2026:3576
- https://access.redhat.com/errata/RHSA-2026:3577
- https://access.redhat.com/errata/RHSA-2026:3968
- https://access.redhat.com/errata/RHSA-2026:3969
- https://access.redhat.com/errata/RHSA-2026:4221
- https://access.redhat.com/errata/RHSA-2026:4222
