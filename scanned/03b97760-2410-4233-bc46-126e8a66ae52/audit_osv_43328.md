# [H] Prowler: Server-Side Request Forgery (SSRF) in Lighthouse Provider

## Summary
Severity: High
Advisory: CVE-2026-73264
Aliases: GHSA-fhj4-q47f-w7mv
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73264
Type: osv

## Details
Prowler is a cloud security platform. Prior to 5.33.1, an authenticated user with Lighthouse provider configuration access could supply an unvalidated base_url for the openai_compatible provider through POST /api/v1/lighthouse/providers and POST /api/v1/lighthouse/providers/{id}/connection, causing api/src/backend/tasks/jobs/lighthouse_providers.py to send outbound requests, including the API key in the Authorization header, to attacker-controlled or internal endpoints when client.models.list was called. This issue is fixed in version 5.33.1.

## References
- https://github.com/prowler-cloud/prowler/releases/tag/5.33.1
- https://github.com/prowler-cloud/prowler/releases/tag/5.34.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73264.json
- https://github.com/prowler-cloud/prowler/security/advisories/GHSA-fhj4-q47f-w7mv
- https://nvd.nist.gov/vuln/detail/CVE-2026-73264
- https://github.com/prowler-cloud/prowler/commit/1c4d8e3e756ee04367353101af797004d1c0258f
- https://github.com/prowler-cloud/prowler/commit/3f2e5929d9ff3c1a5d2fae49f8edd419ee99a8e2
- https://github.com/prowler-cloud/prowler/pull/11928
- https://github.com/prowler-cloud/prowler/pull/11940
