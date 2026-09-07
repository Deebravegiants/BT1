# [C] Cotonti: Cross-Site Request Forgery in the administration rights handler

## Summary
Severity: Critical
Advisory: GHSA-7g3p-35vc-mgjr
CVE: CVE-2026-55742
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-7g3p-35vc-mgjr
Type: github-advisory

## Affected
- Packagist: `cotonti/cotonti` — affected >=0

## Details
Cotonti 1.0.0 (master branch, commit f43f1fc3) is vulnerable to Cross-Site Request Forgery in the administration rights handler. In system/admin/admin.rights.php, the rights update action ('a=update') modifies group access rights (including via cot_auth_add_group) without calling cot_check_xg() to validate the anti-CSRF token. A remote attacker who lures an authenticated administrator into visiting a malicious page can force the browser to submit a forged request that grants elevated permissions to an attacker-controlled group, escalating privileges to administrator. Because Cotonti administrators can modify templates and configuration, this can be further leveraged toward remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-55742
- https://github.com/Cotonti/Cotonti
- https://github.com/Cotonti/Cotonti/blob/f43f1fc38ba4e02027786dad9dac1435c7c52b30/system/admin/admin.rights.php#L53
