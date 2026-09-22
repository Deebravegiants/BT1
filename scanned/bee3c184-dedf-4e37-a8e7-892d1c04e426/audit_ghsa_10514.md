# [H] n8n Vulnerable to XSS via MCP OAuth client

## Summary
Severity: High
Advisory: GHSA-537j-gqpc-p7fq
CVE: CVE-2026-42235
CWE: CWE-79, CWE-87
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-537j-gqpc-p7fq
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.32
- npm: `n8n` — affected >=2.18.0 <2.18.1
- npm: `n8n` — affected >=2.17.0 <2.17.4

## Details
## Impact
An unauthenticated attacker could register a malicious MCP OAuth client with a crafted `client_name`. If a victim user authorized the OAuth consent dialog and a second user subsequently revoked that access, a toast notification would render the injected script. Clicking the link would execute arbitrary JavaScript in the victim's authenticated n8n browser session, enabling credential and session token theft, workflow manipulation, or privilege escalation.

## Patches
This issue has been fixed in n8n version 2.14.2. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict access to the n8n instance and the MCP OAuth registration endpoint to trusted users only.
- Disable MCP server functionality if it is not actively required.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-537j-gqpc-p7fq
- https://nvd.nist.gov/vuln/detail/CVE-2026-42235
- https://github.com/n8n-io/n8n
