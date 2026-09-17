# [M] libvips: A well-crafted PPM image processed via a custom source could lead to possible heap buffer write overflow

## Summary
Severity: Medium
Advisory: CVE-2026-70654
Aliases: GHSA-rjmm-3qch-m9rg
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-70654
Type: osv

## Details
libvips is a fast image processing library with low memory needs. Prior to version 8.18.3, applications that define unusual custom libvips sources and use them to process untrusted uncompressed PPM images can trigger a max/min error in vips_source_read_to_memory in libvips/iofuncs/source.c. The function uses VIPS_MAX instead of VIPS_MIN when selecting the remaining read size, allowing up to 4032 bytes to be written beyond the allocated heap buffer and causing memory corruption or a process crash. This issue is fixed in version 8.18.3.

## References
- https://github.com/libvips/libvips/releases/tag/v8.18.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70654.json
- https://github.com/libvips/libvips/security/advisories/GHSA-rjmm-3qch-m9rg
- https://nvd.nist.gov/vuln/detail/CVE-2026-70654
- https://github.com/libvips/libvips/commit/80e021c6cdda0f80b756c2109d99839c94c03258
- https://github.com/libvips/libvips/pull/5038
