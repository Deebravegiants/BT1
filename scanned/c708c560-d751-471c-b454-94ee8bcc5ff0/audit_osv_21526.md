# [H] CVE-2021-43778

## Summary
Severity: High
Advisory: CVE-2021-43778
Aliases: GHSA-2pjh-h828-wcw9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-11-24
Source: https://osv.dev/vulnerability/CVE-2021-43778
Type: osv

## Details
Barcode is a GLPI plugin for printing barcodes and QR codes. GLPI instances version 2.x prior to version 2.6.1 with the barcode plugin installed are vulnerable to a path traversal vulnerability. This issue was patched in version 2.6.1. As a workaround, delete the `front/send.php` file.

## References
- https://github.com/hansmach1ne/CVE-portfolio/tree/main/CVE-2021-43778
- https://github.com/pluginsGLPI/barcode/releases/tag/2.6.1
- https://github.com/pluginsGLPI/barcode/commit/428c3d9adfb446e8492b1c2b7affb3d34072ff46
- https://github.com/pluginsGLPI/barcode/security/advisories/GHSA-2pjh-h828-wcw9
- https://github.com/hansmach1ne/MyExploits/tree/main/Path%20Traversal%20in%20GLPI%20Barcode%20plugin
