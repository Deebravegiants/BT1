# [H] libde265 has an out-of-bounds write in process_reference_picture_set via predicted short-term RPS

## Summary
Severity: High
Advisory: CVE-2026-49295
Aliases: GHSA-g2rg-wj66-w594
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-49295
Type: osv

## Details
libde265 is an open source implementation of the h.265 video codec. Prior to version 1.0.20, a crafted H.265 bitstream can cause an out-of-bounds array write in `decoder_context::process_reference_picture_set()` (`libde265/decctx.cc:1376`). The root cause is a missing aggregate bound check on predicted short-term reference picture set entries. Individual list sizes are validated, but the combined count after predicted RPS construction can exceed the 16-entry `PocStFoll` array, writing at index 16. Version 1.0.20 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49295.json
- https://github.com/strukturag/libde265/security/advisories/GHSA-g2rg-wj66-w594
- https://nvd.nist.gov/vuln/detail/CVE-2026-49295
- https://github.com/strukturag/libde265/commit/691f3a3c55b3d32478c4a49895dee061a282652b
