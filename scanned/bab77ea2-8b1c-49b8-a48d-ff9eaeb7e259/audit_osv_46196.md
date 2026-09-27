# [H] A malicious h.265 bitstream can cause an out-of-bounds write in libde265

## Summary
Severity: High
Advisory: JLSEC-2026-789
Ecosystem: Julia
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/JLSEC-2026-789
Type: osv

## Affected
- Julia: `libde265_jll` — affected >=0 <1.1.0+0

## Details
libde265 is an open source implementation of the h.265 video codec. Prior to version 1.0.20, a crafted H.265 bitstream can cause an out-of-bounds array write in `decoder_context::process_reference_picture_set()` (`libde265/decctx.cc:1376`). The root cause is a missing aggregate bound check on predicted short-term reference picture set entries. Individual list sizes are validated, but the combined count after predicted RPS construction can exceed the 16-entry `PocStFoll` array, writing at index 16. Version 1.0.20 patches the issue.

## References
- https://github.com/strukturag/libde265/commit/691f3a3c55b3d32478c4a49895dee061a282652b
- https://github.com/strukturag/libde265/security/advisories/GHSA-g2rg-wj66-w594
