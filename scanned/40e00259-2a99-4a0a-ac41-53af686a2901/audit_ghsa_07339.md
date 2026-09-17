# [H] n8n: Shared Credential Header Leak via HTTP Request Pagination Expression

## Summary
Severity: High
Advisory: GHSA-q3j5-8vrg-4p9q
CVE: CVE-2026-59209
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-q3j5-8vrg-4p9q
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.61
- npm: `n8n` — affected >=2.28.0 <2.28.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.27.4

## Details
## Impact
An authenticated member with use-only editor access to a shared workflow could read credential-populated headers exposed via the `$request` object inside an HTTP Request node's pagination expression. When an HTTP Header Auth credential is applied to a paginated request, the secret is present in `$request.headers` when pagination expressions are evaluated. A user-controlled expression could read that secret, copy it into item data, and exfiltrate it through a later HTTP Request node, bypassing credential domain restrictions, since the secret leaves via item data rather than the credential's own request mechanism.

This issue only affects instances with `N8N_EXPRESSION_ENGINE=vm` set, where paginated HTTP Request workflows using shared credentials are accessible to non-owner users.

## Patches
The issue has been fixed in n8n versions 1.123.61, 2.27.4, and 2.28.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict workflow sharing to fully trusted users only.
- Avoid sharing credentials with use-only access to untrusted users on workflows that use HTTP Request nodes with pagination enabled.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-q3j5-8vrg-4p9q
- https://nvd.nist.gov/vuln/detail/CVE-2026-59209
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n%402.27.4
- https://github.com/n8n-io/n8n/releases/tag/n8n%402.28.1
