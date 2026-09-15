# [H] n8n: Prototype Pollution via Dot-Notation Field Names Leads To Instance-Wide Denial of Service

## Summary
Severity: High
Advisory: GHSA-xwx6-jjhv-84p8
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-xwx6-jjhv-84p8
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.67
- npm: `n8n` — affected >=2.32.0 <2.32.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.31.5

## Details
## Impact

The Edit Fields (Set) node assigned output fields through a dot-notation path setter without restricting the field name, so an authenticated user could name a field after an inherited built-in method path and corrupt a shared global in the main Node.js process. Because that global was used on the request-authentication path, the instance then failed every authenticated request, causing a instance-wide denial of service for all users until the process was restarted.

## Patches

The issue has been fixed in n8n versions 1.123.67, 2.31.5, and 2.32.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds

If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict n8n instance access to fully trusted users only.
- Disable or restrict workflow creation and execution permissions for untrusted users.
- Monitor for unexpected process-wide HTTP 500 errors and restart the process promptly if they occur.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-xwx6-jjhv-84p8
- https://github.com/n8n-io/n8n/commit/f69dfc6dd2178a14ea1624d2e1d403c2e755042f
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.67
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.31.5
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.32.1
