# [H] CVE-2024-41311

## Summary
Severity: High
Advisory: CVE-2024-41311
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2024-10-15
Source: https://osv.dev/vulnerability/CVE-2024-41311
Type: osv

## Details
In Libheif 1.17.6, insufficient checks in ImageOverlay::parse() decoding a heif file containing an overlay image with forged offsets can lead to an out-of-bounds read and write.

## References
- https://gist.github.com/flyyee/79f1b224069842ee320115cafa5c35c0
- https://lists.debian.org/debian-lts-announce/2024/10/msg00025.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41311.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41311
- https://github.com/strukturag/libheif/issues/1226
- https://github.com/strukturag/libheif/commit/a3ed1b1eb178c5d651d6ac619c8da3d71ac2be36
- https://github.com/strukturag/libheif/pull/1227
