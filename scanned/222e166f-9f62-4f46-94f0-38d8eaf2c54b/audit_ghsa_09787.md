# [H] n8n has a Python Task Runner Sandbox Escape Vulnerability

## Summary
Severity: High
Advisory: GHSA-44v6-jhgm-p3m4
CVE: CVE-2026-42234
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-44v6-jhgm-p3m4
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.32
- npm: `n8n` — affected >=2.18.0 <2.18.1
- npm: `n8n` — affected >=2.17.0 <2.17.4

## Details
## Impact
An authenticated user with permission to create or modify workflows containing a Python Code Node could escape the sandbox and achieve arbitrary code execution on the task runner container.

- This issue only affects instances where the Python Task Runner is enabled.

## Patches
The issue has been fixed in n8n versions 1.123.32, 2.17.4, and 2.18.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the Python Code node by adding `n8n-nodes-base.code` to the `NODES_EXCLUDE` environment variable, or disable the Python Task Runner entirely.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-44v6-jhgm-p3m4
- https://nvd.nist.gov/vuln/detail/CVE-2026-42234
- https://github.com/n8n-io/n8n
