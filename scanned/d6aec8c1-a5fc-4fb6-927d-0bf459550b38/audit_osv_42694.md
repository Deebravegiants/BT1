# [H] imagecli - Negative carve Ratio Bypasses Bounds Check and Crashes Process via Reachable Panic

## Summary
Severity: High
Advisory: CVE-2026-70378
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-70378
Type: osv

## Details
imagecli's pipeline operation (Carve::apply in src/image_ops.rs) only asserts , never validating that the ratio is positive. A negative ratio (e.g. -5) causes the computed target width to saturate to 0 via Rust's defined float-to-uint cast, which is then passed to imageproc::seam_carving::shrink_width — a function that panics when given a width below 2, crashing the process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70378.json
- https://github.com/theotherphil/imagecli/issues/67
- https://nvd.nist.gov/vuln/detail/CVE-2026-70378
