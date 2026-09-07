# [H] n8n: Authenticated code execution in the n8n Git node

## Summary
Severity: High
Advisory: GHSA-rcv6-pvrj-4xcg
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-rcv6-pvrj-4xcg
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.67
- npm: `n8n` — affected >=2.32.0 <2.32.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.31.5

## Details
## Impact

Authenticated n8n users with rights to create and execute workflows could achieve code execution on the n8n host. Using the Git node, under the default `git` security settings, by staging a crafted local repository, an attacker could cause `git` to run hooks, executing arbitrary commands as the n8n process user.

Both self-hosted and cloud instances are affected where authenticated users can create and execute workflows using the Git node.

## Patches

The issue has been fixed in n8n versions 1.123.67, 2.31.5, and 2.32.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds

If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict n8n instance access to fully trusted users only.
- Disable the Git node by adding `n8n-nodes-base.git` to the `NODES_EXCLUDE` environment variable.
- Restrict network egress from the n8n instance to limit the impact of arbitrary code execution.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-rcv6-pvrj-4xcg
- https://github.com/n8n-io/n8n/commit/f69dfc6dd2178a14ea1624d2e1d403c2e755042f
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.67
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.31.5
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.32.1
