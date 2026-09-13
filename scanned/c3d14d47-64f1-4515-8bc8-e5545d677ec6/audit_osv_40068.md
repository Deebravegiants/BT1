# [M] libheif: Wrapped icef compressed-unit range check causes out-of-bounds read in uncompressed HEIF decoder

## Summary
Severity: Medium
Advisory: CVE-2026-49271
Aliases: GHSA-r7qj-cg5r-r6vf
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-49271
Type: osv

## Details
libheif is a HEIF and AVIF file format decoder and encoder. Prior to version 1.22.1, the uncompressed HEIF decoder validates explicit icef compressed-unit offsets using unit_offset + unit_size. Because the addition can wrap, a crafted HEIF file can pass the range check and then construct a vector from iterators outside the compressed item buffer, producing an out-of-bounds heap read and crash. Version 1.22.1 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49271.json
- https://github.com/strukturag/libheif/security/advisories/GHSA-r7qj-cg5r-r6vf
- https://nvd.nist.gov/vuln/detail/CVE-2026-49271
