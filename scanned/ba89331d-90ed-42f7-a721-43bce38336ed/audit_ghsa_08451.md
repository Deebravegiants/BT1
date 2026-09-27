# [M] imageproc has fragile bounds check when sampling from image

## Summary
Severity: Medium
Advisory: GHSA-5qv7-j6w5-fr4m
CWE: CWE-190
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-5qv7-j6w5-fr4m
Type: github-advisory

## Affected
- crates.io: `imageproc` — affected >=0.24.0 <0.24.1
- crates.io: `imageproc` — affected >=0.25.0 <0.25.1
- crates.io: `imageproc` — affected >=0.26.0 <0.26.2

## Details
A read of pixels was coded as modifying coordinates to lie within the image bounds. It would calculate a coordinate by adding a constant to an input and taking the minimum of the resulting coordinate and 'dimension - 1'. This would not protect against malicious inputs that could overflow the addition. Following the tricked bounds check, the image could then be sampled at multiple differently calculated coordinates that exceeded the bounds.

## References
- https://github.com/image-rs/imageproc
- https://rustsec.org/advisories/RUSTSEC-2026-0115.html
