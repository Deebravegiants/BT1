# [H] n8n: Prototype Pollution via Workflow Credentials Leads to Unauthenticated User and Project Enumeration

## Summary
Severity: High
Advisory: GHSA-75qm-gp28-rcq9
CVE: CVE-2026-59206
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-75qm-gp28-rcq9
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.61
- npm: `n8n` — affected >=2.28.0 <2.28.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.27.4

## Details
## Impact
An authenticated user with the default `workflow:create` permission could pollute `Object.prototype` through a crafted workflow saved, updated, or imported via the workflow API. This can be leveraged to bypass authentication, allowing unauthenticated requests to be treated as a privileged user and exposing endpoints such as the user and project listings. As a result, every account's personal data (email, role, MFA status) and all projects on the instance may be disclosed to unauthenticated callers. The pollution can also corrupt global state, making parts of the instance unresponsive until restarted.

## Patches
The issue has been fixed in n8n versions 1.123.61, 2.27.4, and 2.28.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict workflow creation and editing permissions to fully trusted users only.
- Restrict network access to the n8n instance to trusted users only.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-75qm-gp28-rcq9
- https://nvd.nist.gov/vuln/detail/CVE-2026-59206
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n%402.27.4
- https://github.com/n8n-io/n8n/releases/tag/n8n%402.28.1
