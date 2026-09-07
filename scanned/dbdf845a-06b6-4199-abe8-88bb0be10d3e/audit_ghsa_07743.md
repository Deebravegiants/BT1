# [H] n8n Vulnerable to Stored XSS via Various Nodes

## Summary
Severity: High
Advisory: GHSA-2p9h-rqjw-gm92
CVE: CVE-2026-27578
CWE: CWE-79, CWE-80
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-2p9h-rqjw-gm92
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.22
- npm: `n8n` — affected >=2.0.0 <2.9.3
- npm: `n8n` — affected >=2.10.0 <2.10.1

## Details
## Impact
An authenticated user with permission to create or modify workflows could inject arbitrary scripts into pages rendered by the n8n application using different techniques on various nodes (Form Trigger node, Chat Trigger node, Send & Wait node, Webhook Node, and Chat Node). Scripts injected by a malicious workflow execute in the browser of any user who visits the affected page, enabling session hijacking and account takeover.

## Patches
The issues have been fixed in n8n versions 2.10.1, 2.9.3, and 1.123.22. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the Webhook node by adding `n8n-nodes-base.webhook` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## Credit
Reporters:
- @ori-ron
- @Aikido-Security
- @nil340
- Pawel Bednarz from the NATO Cyber Security Centre (NCSC)

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-2p9h-rqjw-gm92
- https://nvd.nist.gov/vuln/detail/CVE-2026-27578
- https://github.com/n8n-io/n8n/commit/062644ef786b6af480afe4a0f12bc6d70040534a
- https://github.com/n8n-io/n8n/commit/1479aab2d32fe0ee087f82b9038b1035c98be2f6
- https://github.com/n8n-io/n8n/commit/9e5212ecbc5d2d4e6f340b636a5e84be6369882e
- https://github.com/n8n-io/n8n
