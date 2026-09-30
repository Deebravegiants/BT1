# [M] imageproc: integer overflow in kernel size check leads to out-of-bounds read

## Summary
Severity: Medium
Advisory: GHSA-w5p8-4jcx-2j6r
CWE: CWE-125, CWE-190
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-w5p8-4jcx-2j6r
Type: github-advisory

## Affected
- crates.io: `imageproc` — affected >=0 <0.23.1
- crates.io: `imageproc` — affected >=0.24.0 <0.24.1
- crates.io: `imageproc` — affected >=0.25.0 <0.25.1
- crates.io: `imageproc` — affected >=0.26.0 <0.26.2

## Details
A bounds verification of a slice storage of a 2-dimensional matrix's coefficients (a kernel) would compare the total size against the product of individual dimensions. This would erroneously cast *after* the multiplication and consequently fail to detect possible violations when overflow occurs.

Afterwards, the individual sizes were trusted to properly constrain coordinates within the matrix to indices valid for the underlying storage. With a crafted `Kernel` object, certain combinations of coordinates could then cause an out-of-bounds access in an `unsafe` function while fulfilling its documented preconditions. The kernel value could be passed to library functions that trusted the preconditions and then performed such reads.

## References
- https://github.com/image-rs/imageproc
- https://rustsec.org/advisories/RUSTSEC-2026-0116.html
