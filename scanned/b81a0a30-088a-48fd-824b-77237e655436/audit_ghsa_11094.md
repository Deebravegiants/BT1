# [C] n8n has Multiple Remote Code Execution Vulnerabilities in Merge Node AlaSQL SQL Mode

## Summary
Severity: Critical
Advisory: GHSA-58qr-rcgv-642v
CVE: CVE-2026-33660
CWE: CWE-89, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-58qr-rcgv-642v
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.14.0 <2.14.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.13.3
- npm: `n8n` — affected >=0 <1.123.27

## Details
## Impact
An authenticated user with permission to create or modify workflows could use the Merge node's "Combine by SQL" mode to read local files on the n8n host and achieve remote code execution. The AlaSQL sandbox did not sufficiently restrict certain SQL statements, allowing an attacker to access sensitive files on the server or even compromise the intance.

## Patches
The issue has been fixed in n8n versions 2.14.1, 2.13.3, and 1.123.27. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the Merge node by adding `n8n-nodes-base.merge` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-58qr-rcgv-642v
- https://nvd.nist.gov/vuln/detail/CVE-2026-33660
- https://github.com/n8n-io/n8n
