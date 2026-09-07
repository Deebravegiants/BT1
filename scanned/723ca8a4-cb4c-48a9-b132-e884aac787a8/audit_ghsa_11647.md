# [M] n8n: Authenticated XSS and Open Redirect via Form Node

## Summary
Severity: Medium
Advisory: GHSA-w673-8fjw-457c
CWE: CWE-601, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-w673-8fjw-457c
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.11.0 <2.12.0
- npm: `n8n` — affected >=2.0.0-rc.0 <2.10.4
- npm: `n8n` — affected >=0 <1.123.24

## Details
## Impact
An authenticated user with permission to create or modify workflows could configure a Form Node with an unsanitized HTML description field or exploit an overly permissive iframe sandbox policy to perform stored cross-site scripting or redirect end users visiting the form to an arbitrary external URL. The vulnerability could be used to facilitate phishing attacks.

## Patches
The issue has been fixed in n8n versions 1.123.24, 2.10.4 and 2.12.0. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the Form node by adding `n8n-nodes-base.form` to the `NODES_EXCLUDE` environment variable.
- Disable the Form Trigger node by adding `n8n-nodes-base.formTrigger` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-w673-8fjw-457c
- https://github.com/n8n-io/n8n
