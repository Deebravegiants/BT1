# [H] n8n: Stored DOM XSS via Resource Locator `cachedResultUrl`

## Summary
Severity: High
Advisory: GHSA-9wcp-9r3j-383q
CVE: CVE-2026-65592
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:H/VI:H/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-9wcp-9r3j-383q
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.64
- npm: `n8n` — affected >=2.30.0 <2.30.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.29.8

## Details
## Impact
The Resource Locator passes the workflow-persisted `cachedResultUrl` to `window.open()` without scheme validation. When a victim opens the crafted workflow and interact with external links, the JavaScript payload runs in the victim's browser. 

## Patches
The issue has been fixed in n8n versions 1.123.64, 2.29.8, and 2.30.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict workflow creation and editing permissions to fully trusted users only.
- Audit existing workflows for unexpected `cachedResultUrl` values containing non-HTTP(S) schemes.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-9wcp-9r3j-383q
- https://nvd.nist.gov/vuln/detail/CVE-2026-65592
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.64
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.29.8
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.30.1
- https://www.vulncheck.com/advisories/n8n-before-stored-dom-xss-via-cachedresulturl
