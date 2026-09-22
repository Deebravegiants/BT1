# [M] LIBPNG: Chunk smuggling in push-mode APNG parser via unconsumed chunk body

## Summary
Severity: Medium
Advisory: CVE-2026-40930
Aliases: GHSA-c4v6-gxrq-6g2x
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2026-06-04
Source: https://osv.dev/vulnerability/CVE-2026-40930
Type: osv

## Details
LIBPNG is a reference library for use in applications that process PNG (Portable Network Graphics) raster image files. In version 1.8.0, three inter-frame chunk discard paths in the push-mode APNG parser clear the chunk-header flag without consuming the chunk body and CRC, allowing attacker-controlled bytes inside an ignored ancillary chunk to be reinterpreted as a fresh chunk header on the next call to `png_process_data`. Commit faf06924688b62d7c1654b5ceddedbde66ffadb4 fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/05/15/21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40930.json
- https://github.com/pnggroup/libpng/security/advisories/GHSA-c4v6-gxrq-6g2x
- https://nvd.nist.gov/vuln/detail/CVE-2026-40930
- https://github.com/pnggroup/libpng/commit/faf06924688b62d7c1654b5ceddedbde66ffadb4
