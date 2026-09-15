# [M] ALPINE-CVE-2026-40930

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-40930
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2026-06-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-40930
Type: osv

## Affected
- Alpine:v3.23: `libpng` — affected >=0 <1.6.58-r1
- Alpine:v3.24: `libpng` — affected >=0 <1.6.58-r1

## Details
LIBPNG is a reference library for use in applications that process PNG (Portable Network Graphics) raster image files. In version 1.8.0, three inter-frame chunk discard paths in the push-mode APNG parser clear the chunk-header flag without consuming the chunk body and CRC, allowing attacker-controlled bytes inside an ignored ancillary chunk to be reinterpreted as a fresh chunk header on the next call to `png_process_data`. Commit faf06924688b62d7c1654b5ceddedbde66ffadb4 fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-40930
