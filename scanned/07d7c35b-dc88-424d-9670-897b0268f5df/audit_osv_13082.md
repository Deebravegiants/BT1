# [M] CVE-2018-17292

## Summary
Severity: Medium
Advisory: CVE-2018-17292
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-21
Source: https://osv.dev/vulnerability/CVE-2018-17292
Type: osv

## Details
An issue was discovered in WAVM before 2018-09-16. The loadModule function in Include/Inline/CLI.h lacks checking of the file length before a file magic comparison, allowing attackers to cause a Denial of Service (application crash caused by out-of-bounds read) by crafting a file that has fewer than 4 bytes.

## References
- https://github.com/WAVM/WAVM/commit/2de6cf70c5ef31e22ed119a25ac2daeefd3d18a1
- https://github.com/WAVM/WAVM/issues/109
