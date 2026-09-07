# [M] Webkul Krayin CRM is Vulnerable to Cross-Site Scripting in the /admin/activities/create endpoint

## Summary
Severity: Medium
Advisory: GHSA-j822-46r5-h4qx
CVE: CVE-2026-36341
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-j822-46r5-h4qx
Type: github-advisory

## Affected
- Packagist: `krayin/laravel-crm` — affected >=2.1.5 <2.1.6

## Details
Cross-Site Scripting (XSS) vulnerability exists in Webkul Krayin CRM v2.1.5. The application fails to sanitize user-supplied input in the comment field during Activity creation on the /admin/activities/create endpoint

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-36341
- https://github.com/krayin/laravel-crm/pull/2401
- https://github.com/krayin/laravel-crm/commit/fc467040de21803cb2b67c2229d2dfcf731d2d3e
- https://cyber.spool.co.jp/vulnerabilities/cve-2026-36341
- https://drive.google.com/file/d/1Y_WjD4Tiq_z7zQUlddFCFMDoyyN300r9/view
- https://github.com/cybercrewinc/CVE-2026-36341
- https://github.com/krayin/laravel-crm
- https://github.com/krayin/laravel-crm/releases/tag/v2.1.6
