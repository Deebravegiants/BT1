# [M] OAuth token exchange grants repository scopes for organizations the principal cannot access

## Summary
Severity: Medium
Advisory: CVE-2026-75542
Aliases: EEF-CVE-2026-75542, GHSA-rfx8-w654-8cpr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-75542
Type: osv

## Details
Incorrect Authorization vulnerability in the OAuth token endpoint in hexpm hexpm allows an API key holding the repositories permission to read another organization's private packages.

When an API key is exchanged for a token through the OAuth client_credentials grant, validate_scopes_against_key/2 in lib/hexpm_web/controllers/api/oauth_controller.ex admits a requested scope whenever the key carries the repositories permission and the scope string begins with repository:. The organization name is never resolved against the principal, and expand_repositories_scope/3 only rewrites the literal repositories scope, so an explicit repository:<name> passes through untouched. Both CDN edges authorize repository access from the token claim without querying the database, so the minted token is read access to that organization's private packages until it expires.

This issue affects hex.pm: from 2025-10-18 before 2026-08-24.

## References
- https://cna.erlef.org/cves/CVE-2026-75542.html
- https://github.com
- https://hex.pm
- https://osv.dev/vulnerability/EEF-CVE-2026-75542
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75542.json
- https://github.com/hexpm/hexpm/security/advisories/GHSA-rfx8-w654-8cpr
- https://nvd.nist.gov/vuln/detail/CVE-2026-75542
- https://github.com/hexpm/hexpm/commit/bf0fb9d208f0acfabf7a2f7467c8231659e322a8
- https://github.com/hexpm/hexpm
