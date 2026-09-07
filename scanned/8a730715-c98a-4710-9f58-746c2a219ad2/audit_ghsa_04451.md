# [M] n8n: Reflected XSS via Facebook, WhatsApp, and Microsoft Teams Trigger Webhook Verification Endpoints

## Summary
Severity: Medium
Advisory: GHSA-h86q-fx34-gfjr
CVE: CVE-2026-54303
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-h86q-fx34-gfjr
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <2.24.0

## Details
## Impact
An endpoint in the Meta and Microsoft Teams trigger nodes reflects a query parameter into the HTTP response without sanitization or Content-Security-Policy headers, enabling reflected XSS in the n8n origin when a logged-in user visits a crafted URL.

## Patches
The issue has been fixed in n8n version 2.24.0. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and activation permissions to fully trusted users only.
- Disable the affected nodes by adding `n8n-nodes-base.facebookTrigger`, `n8n-nodes-base.whatsAppTrigger`, `n8n-nodes-base.facebookLeadAdsTrigger`, and `n8n-nodes-base.microsoftTeamsTrigger` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-h86q-fx34-gfjr
- https://nvd.nist.gov/vuln/detail/CVE-2026-54303
- https://github.com/n8n-io/n8n
