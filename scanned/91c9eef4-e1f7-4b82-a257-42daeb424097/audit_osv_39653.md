# [H] Vvveb: admin/auth-token IDOR allows unauthorized disclosure of administrator REST API tokens

## Summary
Severity: High
Advisory: CVE-2026-46407
Aliases: GHSA-5g3g-x6mf-pwr6
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-46407
Type: osv

## Details
Vvveb is a powerful and easy to use CMS with page builder to build websites, blogs or ecommerce stores. Prior to 1.0.8.3, the backend admin/auth-token endpoint allows an authenticated administrator to load another administrator's REST API token list by supplying that user's admin_id. This can disclose sensitive API tokens belonging to other administrators. This vulnerability is fixed in 1.0.8.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46407.json
- https://github.com/givanz/Vvveb/security/advisories/GHSA-5g3g-x6mf-pwr6
- https://nvd.nist.gov/vuln/detail/CVE-2026-46407
