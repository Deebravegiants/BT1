# [M] CVE-2025-5683

## Summary
Severity: Medium
Advisory: CVE-2025-5683
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-06-05
Source: https://osv.dev/vulnerability/CVE-2025-5683
Type: osv

## Details
When loading a specifically crafted ICNS format image file in QImage then it will trigger a crash. 

This issue affects Qt from versions 6.3.0 through 6.5.9, from 6.6.0 through 6.8.4, 6.9.0. This is fixed in 6.5.10, 6.8.5 and 6.9.1.

## References
- https://codereview.qt-project.org/c/qt/qtimageformats/+/644548
- https://issues.oss-fuzz.com/issues/415350704
