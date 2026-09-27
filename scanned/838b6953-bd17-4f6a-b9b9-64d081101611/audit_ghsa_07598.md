# [H] n8n has Arbitrary File Read via Python Code Node Sandbox Escape

## Summary
Severity: High
Advisory: GHSA-mmgg-m5j7-f83h
CVE: CVE-2026-27494
CWE: CWE-497
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-mmgg-m5j7-f83h
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.22
- npm: `n8n` — affected >=2.0.0 <2.9.3
- npm: `n8n` — affected >=2.10.0 <2.10.1

## Details
## Impact
An authenticated user with permission to create or modify workflows could use the Python Code node to escape the sandbox. The sandbox did not sufficiently restrict access to certain built-in Python objects, allowing an attacker to exfiltrate file contents or achieve RCE.

On instances using internal Task Runners (default runner mode), this could result in full compromise of the n8n host. On instances using external Task Runners, the attacker might gain access to or impact other task executed on the Task Runner.

- Task Runners must be enabled using `N8N_RUNNERS_ENABLED=true`.

## Patches
The issue has been fixed in n8n versions 2.10.1, 2.9.3, and 1.123.22. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds

If upgrading is not immediately possible, administrators should consider the following temporary mitigations:

- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the Code node by adding `n8n-nodes-base.code` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-mmgg-m5j7-f83h
- https://nvd.nist.gov/vuln/detail/CVE-2026-27494
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.22
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.10.1
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.9.3
