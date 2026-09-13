# [M] Wallos: Cross-user Fixer/API Layer credential consumption in exchange-rate refresh

## Summary
Severity: Medium
Advisory: CVE-2026-50199
Aliases: GHSA-5wf4-m4hj-rxj5
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-50199
Type: osv

## Details
Wallos is an open-source, self-hostable personal subscription tracker. Prior to version 4.9.1, endpoints/currency/update_exchange.php loads the first Fixer/API Layer credential globally instead of loading the credential for the authenticated user. As a result, a normal authenticated user without their own provider key can trigger exchange-rate refreshes using another user's stored provider credential. This issue has been patched in version 4.9.1.

## References
- https://github.com/ellite/Wallos/releases/tag/v4.9.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50199.json
- https://github.com/ellite/Wallos/security/advisories/GHSA-5wf4-m4hj-rxj5
- https://nvd.nist.gov/vuln/detail/CVE-2026-50199
