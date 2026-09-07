# [H] n8n: Send Email Node Arbitrary File Read and SSRF via Nodemailer Content-Object Type Confusion

## Summary
Severity: High
Advisory: GHSA-2x35-3fw4-9jr4
CWE: CWE-200, CWE-843, CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-2x35-3fw4-9jr4
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.67
- npm: `n8n` — affected >=2.32.0 <2.32.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.31.5

## Details
## Impact

The n8n Send Email node did not enforce that its message fields were strings, so a crafted untrusted non-string value from a workflow expression could be treated by the underlying mail library as a file path or URL. This could allow disclosure of local files on the n8n host.

Exploitation requires a pre-existing active workflow with an unauthenticated webhook, valid SMTP credentials configured on the Send Email node, and untrusted input mapped directly into the text or HTML body field. This is not a default n8n configuration.

## Patches

The issue has been fixed in n8n versions 1.123.67, 2.31.5, and 2.32.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds

If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Audit active workflows for Send Email nodes that map untrusted webhook or external data directly into the text or HTML body fields, and remove or restrict those workflows.
- Restrict public webhook access at the network or reverse-proxy level to prevent unauthenticated callers from reaching sensitive workflows.
- Restrict workflow creation and editing permissions to fully trusted users only.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-2x35-3fw4-9jr4
- https://github.com/n8n-io/n8n/commit/f69dfc6dd2178a14ea1624d2e1d403c2e755042f
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.67
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.31.5
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.32.1
