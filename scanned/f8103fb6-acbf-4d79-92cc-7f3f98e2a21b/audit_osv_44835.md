# [H] Snipe-IT before 8.7.0 Authorization Bypass via OAuth Clients

## Summary
Severity: High
Advisory: CVE-2026-86754
Aliases: GHSA-gq7g-hxjg-8j27
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86754
Type: osv

## Details
Snipe-IT before 8.7.0 fails to properly gate Laravel Passport's OAuth client management routes, allowing any authenticated user to register OAuth clients with attacker-controlled redirect URIs. Attackers can trick administrators into approving consent screens, then exchange authorization codes for bearer tokens inheriting full admin API permissions lasting up to 40 years.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86754.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-gq7g-hxjg-8j27
- https://nvd.nist.gov/vuln/detail/CVE-2026-86754
- https://www.vulncheck.com/advisories/snipe-it-before-8.7.0-authorization-bypass-via-oauth-clients
