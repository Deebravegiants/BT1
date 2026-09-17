# [C] n8n has a Sandbox Escape in its JavaScript Task Runner

## Summary
Severity: Critical
Advisory: GHSA-jjpj-p2wh-qf23
CVE: CVE-2026-27495
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-jjpj-p2wh-qf23
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.22
- npm: `n8n` — affected >=2.0.0 <2.9.3
- npm: `n8n` — affected >=2.10.0 <2.10.1

## Details
## Impact
An authenticated user with permission to create or modify workflows could exploit a vulnerability in the JavaScript Task Runner sandbox to execute arbitrary code outside the sandbox boundary.

On instances using internal Task Runners (default runner mode), this could result in full compromise of the n8n host. On instances using external Task Runners, the attacker might gain access to or impact other task executed on the Task Runner.
- Task Runners must be enabled using `N8N_RUNNERS_ENABLED=true`.

## Patches
The issue has been fixed in n8n versions 2.10.1, 2.9.3, and 1.123.22. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Use external runner mode (`N8N_RUNNERS_MODE=external`) to limit the blast radius.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## Resources
- [n8n Documentation — Task Runners](https://docs.n8n.io/hosting/configuration/task-runners/)

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-jjpj-p2wh-qf23
- https://nvd.nist.gov/vuln/detail/CVE-2026-27495
- https://docs.n8n.io/hosting/configuration/task-runners
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.22
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.10.1
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.9.3
