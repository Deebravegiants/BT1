# [C] Cotonti CSRF in admin.config.php allows unauthorized configuration changes

## Summary
Severity: Critical
Advisory: CVE-2026-55741
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-55741
Type: osv

## Details
Cotonti 1.0.0 (master branch, commit f43f1fc3) is vulnerable to Cross-Site Request Forgery in the administration configuration handler. In system/admin/admin.config.php, the configuration update action ('a=update') processes POST data via cot_config_update_options without calling cot_check_xg to validate the anti-CSRF token (the 'x' parameter), unlike other admin handlers (e.g. admin.structure.php, admin.cache.php).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55741.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-55741
- https://github.com/Cotonti/Cotonti
- https://github.com/Cotonti/Cotonti/blob/f43f1fc38ba4e02027786dad9dac1435c7c52b30/system/admin/admin.config.php#L55
