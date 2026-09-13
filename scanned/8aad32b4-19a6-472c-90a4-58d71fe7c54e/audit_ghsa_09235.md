# [M] imageproc: Out-of-bounds read via NaN coordinates in bilinear/bicubic sampling

## Summary
Severity: Medium
Advisory: GHSA-qg8r-f7x3-25f7
CWE: CWE-190
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-qg8r-f7x3-25f7
Type: github-advisory

## Affected
- crates.io: `imageproc` — affected >=0 <0.23.1
- crates.io: `imageproc` — affected >=0.24.0 <0.24.1
- crates.io: `imageproc` — affected >=0.25.0 <0.25.1
- crates.io: `imageproc` — affected >=0.26.0 <0.26.2

## Details
A bounds check was performed in floating points before a cast to the index passed to an unchecked access function. This checked considered `NaN` cases improperly, causing them to succeed the check instead of failing it. The floating point coordinate is under caller control by passing a selected projection matrix.

Carefully controlling the coordinates of an image with no data and one non-zero dimension provides an arbitrary read primitive in the first 32-bits of address space with a Bilinear sampling method.

Using bicubic sampling can result in a read of a few bytes beyond an allocation.

Other out-of-bounds reads may be possible.

## References
- https://github.com/image-rs/imageproc
- https://rustsec.org/advisories/RUSTSEC-2026-0117.html
