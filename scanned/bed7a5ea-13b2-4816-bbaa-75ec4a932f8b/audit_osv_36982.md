# [H] FreeScout: Missing .htaccess in Restricted File Extensions Allows Remote Code Execution on Apache

## Summary
Severity: High
Advisory: CVE-2026-27636
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27636
Type: osv

## Details
FreeScout is a free help desk and shared inbox built with PHP's Laravel framework. Prior to version 1.8.206, FreeScout's file upload restriction list in `app/Misc/Helper.php` does not include `.htaccess` or `.user.ini` files. On Apache servers with `AllowOverride All` (a common configuration), an authenticated user can upload a `.htaccess` file to redefine how files are processed, enabling Remote Code Execution. This vulnerability can be exploited on its own or in combination with CVE-2026-27637. Version 1.8.206 fixes both vulnerabilities.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27636.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-6gcm-v8xf-j9v9
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-mw88-x7j3-74vc
- https://nvd.nist.gov/vuln/detail/CVE-2026-27636
- https://github.com/freescout-help-desk/freescout/commit/9984071e6f1b4e633fdcffcea82bbebc9c1e009c
