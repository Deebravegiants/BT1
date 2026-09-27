# [H] libvips: Integer overflow leading to heap buffer overflow leading to possible attacker-controlled mmap-resident write

## Summary
Severity: High
Advisory: CVE-2026-69242
Aliases: GHSA-9rwc-f68v-4482
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:H/SC:L/SI:H/SA:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-69242
Type: osv

## Details
libvips is a fast image processing library with low memory needs. Prior to version 8.18.3, a crafted many-band TIFF processed through VipsForeignLoadTiff can evade scanline validation in libvips/iofuncs/image.c and cause an integer overflow in vips_image_sanity. The resulting buffer-region calculation can access attacker-controlled negative offsets in mmap-resident allocations, allowing reads or writes of other image data, possible data disclosure through uncompressed .v output, and likely process crashes. Remote code execution has not been demonstrated but cannot be ruled out. This issue is fixed in version 8.18.3.

## References
- https://github.com/libvips/libvips/releases/tag/v8.18.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69242.json
- https://github.com/libvips/libvips/security/advisories/GHSA-9rwc-f68v-4482
- https://nvd.nist.gov/vuln/detail/CVE-2026-69242
- https://github.com/libvips/libvips/commit/c72f50927413cd2451837d9813f954bc5d88f548
- https://github.com/libvips/libvips/pull/5012
