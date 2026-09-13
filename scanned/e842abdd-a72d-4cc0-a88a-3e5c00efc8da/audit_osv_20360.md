# [C] CVE-2021-33199

## Summary
Severity: Critical
Advisory: CVE-2021-33199
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-12
Source: https://osv.dev/vulnerability/CVE-2021-33199
Type: osv

## Details
In Expression Engine before 6.0.3, addonIcon in Addons/file/mod.file.php relies on the untrusted input value of input->get('file') instead of the fixed file names of icon.png and icon.svg.

## References
- https://github.com/ExpressionEngine/ExpressionEngine/releases/tag/6.0.3
- https://github.com/ExpressionEngine/ExpressionEngine/compare/6.0.1...6.0.3#diff-17bcb23e5666fc2dccb79c7133e9eeb701847f67ae84fbde0a673c3fd3d109e0R508
