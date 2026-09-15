# [H] n8n: Python sandbox escape

## Summary
Severity: High
Advisory: GHSA-9pq8-m8gp-4p53
CVE: CVE-2026-49444
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-9pq8-m8gp-4p53
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.48
- npm: `n8n` — affected >=2.22.0 <2.22.4
- npm: `n8n` — affected >=2.0.0-rc.0 <2.21.8

## Details
## Impact
An authenticated user with permission to create or modify workflows containing a Python Code Node could escape the sandbox and achieve arbitrary code execution on the task runner container.

This issue only affects instances where the Python Task Runner is enabled.

## Patches
The issue has been fixed in n8n versions 1.123.48, 2.21.8, and 2.22.4. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the Python Code node by adding `n8n-nodes-base.code` to the `NODES_EXCLUDE` environment variable, or disable the Python Task Runner entirely.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-9pq8-m8gp-4p53
- https://nvd.nist.gov/vuln/detail/CVE-2026-49444
- https://github.com/n8n-io/n8n
