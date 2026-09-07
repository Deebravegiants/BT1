# [H] n8n: Race Condition in Git Clone Node Allows Authenticated Users to Achieve Remote Code Execution

## Summary
Severity: High
Advisory: GHSA-g3r5-9h93-4j2c
CVE: CVE-2026-65598
CWE: CWE-367
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:L/SA:L (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-g3r5-9h93-4j2c
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.64
- npm: `n8n` — affected >=2.30.0 <2.30.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.29.8

## Details
## Impact
A TOCTOU race condition in the Git node's `clone` operation lets an authenticated user bypass its path restrictions by swapping a directory for a symlink after the path is validated but before the clone runs. This plants a crafted repository in the community node directory, which n8n loads as a custom node on the next restart, and since nodes execute JavaScript, this yields arbitrary code execution on the server.

Both self-hosted and cloud instances are affected, where authenticated users can create and run workflows using the Git node.

## Patches
Users should upgrade to the patched version once available to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict n8n instance access to fully trusted users only.
- Disable the Git node by adding `n8n-nodes-base.git` to the `NODES_EXCLUDE` environment variable.
- Restrict network egress from the n8n instance to prevent connections to attacker-controlled git repositories.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-g3r5-9h93-4j2c
- https://nvd.nist.gov/vuln/detail/CVE-2026-65598
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.64
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.29.8
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.30.1
- https://www.vulncheck.com/advisories/n8n-before-remote-code-execution-via-git-clone
