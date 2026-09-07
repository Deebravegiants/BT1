# [M] n8n: Path-Confinement Bypass in computer-use search_files Allows Reading Files Outside the Base Directory

## Summary
Severity: Medium
Advisory: GHSA-pf2q-pxhf-hgmw
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-pf2q-pxhf-hgmw
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.32.0 <2.32.1
- npm: `n8n` — affected >=0 <2.31.5

## Details
## Impact

The component `@n8n/computer-use` file-search tool confined searches to a configured base directory. A crafted search pattern could bypass the confinement check and expand to locations outside that directory, causing the tool to return the names and contents of files anywhere the daemon's OS user could read. Any deployment where an actor could influence the tool's search input was affected; the result was disclosure of arbitrary local files outside the intended sandbox.

## Patches

The issue has been fixed in n8n versions 2.31.5 and 2.32.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds

If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict n8n instance access to fully trusted users only.
- Disable or remove AI agent workflows that use the `computer-use` package until the instance is patched.
- Ensure the n8n process runs under a dedicated low-privilege user account to limit the files accessible outside the sandbox.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-pf2q-pxhf-hgmw
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.31.5
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.32.1
