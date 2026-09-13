# [H] Dokploy: Unauthenticated Git Provider Injection via GitHub OAuth Callback

## Summary
Severity: High
Advisory: CVE-2026-72871
Aliases: GHSA-g9pp-xcf2-ph7x
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72871
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, the unauthenticated /api/providers/github/setup route in apps/dokploy/pages/api/providers/github/setup.ts trusts gh_init organizationId and userId values from the state parameter and calls createGithub in packages/server/src/services/github.ts, allowing an attacker to insert a GitHub App provider containing client_secret, webhook_secret, and PEM private key material into another organization. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72871.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-g9pp-xcf2-ph7x
- https://nvd.nist.gov/vuln/detail/CVE-2026-72871
- https://github.com/Dokploy/dokploy/commit/5ae344db5814bfdcd700c5cc8ee8eb1a23af7253
- https://github.com/Dokploy/dokploy/pull/4870
