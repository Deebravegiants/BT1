# [M] n8n: Unauthenticated Endpoint Allows Cancellation of Any User's Active Test Webhook

## Summary
Severity: Medium
Advisory: GHSA-33q9-f52j-gc75
CVE: CVE-2026-65014
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-33q9-f52j-gc75
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <2.27.4

## Details
## Impact
The `DELETE /${restEndpoint}/test-webhook/:id` route is registered before the authentication middleware is applied, allowing any unauthenticated network caller who knows a workflow ID to cancel that workflow's active test webhook registration. 

The impact is limited to disrupting in-progress test sessions. Production webhooks, persistent workflow state, and stored data are not affected.

## Patches
Users should upgrade to the patched version once available to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict network access to the n8n instance to fully trusted users only.
- Place the n8n instance behind a reverse proxy or firewall that requires authentication before reaching the REST API.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-33q9-f52j-gc75
- https://nvd.nist.gov/vuln/detail/CVE-2026-65014
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.27.4
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.28.0
- https://www.vulncheck.com/advisories/n8n-before-authentication-bypass-via-test-webhook
