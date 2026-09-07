# [M] n8n: computer-use Shell Sandbox Not Enforced on Linux and Windows

## Summary
Severity: Medium
Advisory: GHSA-fpg6-x68q-5793
CVE: CVE-2026-65590
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-fpg6-x68q-5793
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.30.0 <2.30.1
- npm: `n8n` — affected >=0 <2.29.8

## Details
## Impact
The shell tool in the `@n8n/computer-use` package applied its sandbox restrictions only on macOS. On Linux and Windows, shell commands executed by the tool ran without any filesystem or network restrictions, allowing unrestricted access to the host filesystem and network from within the computer-use agent process.

This issue only affects deployments where the `@n8n/computer-use` package is explicitly installed and running. It does not affect standard n8n installations.

## Patches
The issue has been fixed in n8n versions 2.29.8 and 2.30.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

The fix adds sandbox enforcement on Linux via bubblewrap and disables the shell tool entirely when a working sandbox cannot be established. An explicit opt-out flag (`--dangerously-disable-shell-sandbox`) is available for deployments that require unsandboxed shell access and accept the associated risk.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Disable or avoid deploying the `@n8n/computer-use` package on Linux or Windows hosts until the fix is applied.
- Restrict access to the n8n instance and the computer-use agent to fully trusted users only.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-fpg6-x68q-5793
- https://nvd.nist.gov/vuln/detail/CVE-2026-65590
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.29.8
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.30.1
- https://www.vulncheck.com/advisories/n8n-before-shell-sandbox-bypass-on-linux-windows
