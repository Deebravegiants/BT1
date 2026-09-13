# [H] n8n: Legacy Expression Evaluator Sanitizer Bypass Leads to Authenticated Code Execution

## Summary
Severity: High
Advisory: GHSA-pm35-fqvh-cq5g
CVE: CVE-2026-65591
CWE: CWE-917
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:L (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-pm35-fqvh-cq5g
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.64
- npm: `n8n` — affected >=2.30.0 <2.30.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.29.8

## Details
## Impact
The legacy expression evaluator's computed-member sanitizer can be bypassed by an authenticated user with workflow create or modify permissions. Successful exploitation grants the attacker host-level code execution as the n8n process.

The legacy expression engine is the default engine in affected versions.

## Patches
The issue has been fixed in n8n versions 1.123.64, 2.29.8, and 2.30.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict n8n instance access to fully trusted users only.
- Switch to the non-legacy expression engine by setting `N8N_EXPRESSION_ENGINE=vm`.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-pm35-fqvh-cq5g
- https://nvd.nist.gov/vuln/detail/CVE-2026-65591
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.64
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.29.8
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.30.1
- https://www.vulncheck.com/advisories/n8n-before-sanitizer-bypass-remote-code-execution
