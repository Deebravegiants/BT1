# [H] QuickAppsCMS Cross-Site Request Forgery (CSRF) 

## Summary
Severity: High
Advisory: GHSA-62g2-8p9f-ghjp
CVE: CVE-2018-9108
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-62g2-8p9f-ghjp
Type: github-advisory

## Affected
- Packagist: `quickapps/cms` — affected 2.0.0-beta2

## Details
CSRF in `/admin/user/manage/add` in QuickAppsCMS 2.0.0-beta2 allows an unauthorized remote attacker to create an account with admin privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-9108
- https://github.com/quickapps/cms/issues/187
- https://github.com/quickapps/cms
