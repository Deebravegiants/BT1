# [H] n8n: Edit Image Node Format Injection Allows Arbitrary File Write

## Summary
Severity: High
Advisory: GHSA-xmc9-4f2h-jf9c
CWE: CWE-73
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-xmc9-4f2h-jf9c
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.67
- npm: `n8n` — affected >=2.32.0 <2.32.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.31.5

## Details
## Impact

The n8n Edit Image node passed its output format to the underlying image library without validation, so a crafted value could write bytes to a location outside the node's working directory. An authenticated user able to run workflows could use this to write arbitrary files in the n8n instance.

## Patches

The issue has been fixed in n8n versions 1.123.67, 2.31.5, and 2.32.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds

If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict n8n instance access to fully trusted users only.
- Disable the Edit Image node by adding `n8n-nodes-base.editImage` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-xmc9-4f2h-jf9c
- https://github.com/n8n-io/n8n/commit/f69dfc6dd2178a14ea1624d2e1d403c2e755042f
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.67
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.31.5
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.32.1
