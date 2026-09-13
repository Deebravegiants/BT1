# [H] n8n: AI Agents Project Viewer Privilege Escalation via run_node_tool

## Summary
Severity: High
Advisory: GHSA-x5vx-c2c8-m3w9
CVE: CVE-2026-65015
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:L (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-x5vx-c2c8-m3w9
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.30.0 <2.30.1
- npm: `n8n` — affected >=0 <2.29.8

## Details
## Impact
In n8n's AI Agents feature, a user with the read-only Project Viewer role could escalate their privileges by chatting with an agent that has node tools enabled. The agent's node-execution tool was authorized only by the `agent:execute` scope and ran nodes using the project's credentials, without verifying that the requesting user was permitted to execute nodes or to access those credentials.

As a result, a Project Viewer could execute arbitrary tool nodes on the server and use credential secrets they were not authorized to read, gaining execution capabilities their role is intended to deny. On instances where a command- or file-capable tool node (such as Execute Command or SSH) is enabled, this could be extended to arbitrary command execution on the n8n host.

Users of the AI Agents feature who share team projects with lower-privileged members are affected.

## Patches
The issue has been fixed in n8n versions 2.29.8 and 2.30.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Disable the AI Agents module by removing `agents` from the `N8N_ENABLED_MODULES` environment variable.
- Restrict project membership to fully trusted users only, and avoid granting Project Viewer access to untrusted users on projects containing agents with node tools enabled.
- Disable command-execution nodes (e.g. Execute Command, SSH) if they have been re-enabled, to limit the potential impact.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-x5vx-c2c8-m3w9
- https://nvd.nist.gov/vuln/detail/CVE-2026-65015
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.29.8
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.30.1
- https://www.vulncheck.com/advisories/n8n-before-privilege-escalation-via-run-node-tool
