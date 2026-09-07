# [M] n8n: Git Node Clone and Push Operations Bypass File Sandbox

## Summary
Severity: Medium
Advisory: GHSA-5xp3-2w67-427v
CVE: CVE-2026-49465
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-5xp3-2w67-427v
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.48
- npm: `n8n` — affected >=2.22.0 <2.22.4
- npm: `n8n` — affected >=2.0.0-rc.0 <2.21.8

## Details
## Impact
An authenticated user with permission to create or modify workflows could supply a local filesystem path as the source repository in the Git node's Clone operation, or as the target repository in the Push operation, bypassing the `N8N_RESTRICT_FILE_ACCESS_TO` file sandbox. This allowed the contents of any local git repository accessible to the n8n process to be cloned into an allowed path and read, circumventing the access restrictions that correctly blocked direct file reads to the same paths.

## Patches
The issue has been fixed in n8n versions 1.123.48, 2.21.8, and 2.22.4. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the Git node by adding `n8n-nodes-base.git` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-5xp3-2w67-427v
- https://nvd.nist.gov/vuln/detail/CVE-2026-49465
- https://github.com/n8n-io/n8n
