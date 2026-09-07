# [H] n8n: DOM-Based XSS via Unsandboxed iframe srcdoc in HTML Preview

## Summary
Severity: High
Advisory: GHSA-p3rg-hrf9-w9gj
CVE: CVE-2026-65597
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-p3rg-hrf9-w9gj
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.64
- npm: `n8n` — affected >=2.30.0 <2.30.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.29.8

## Details
## Impact

The HTML preview renders execution output into an `iframe srcdoc` without `sandbox`, so a sanitizer bypass lets injected script run same-origin as the editor. When a victim opens the preview, it can call authenticated APIs with their session. An account with `global:member` privileges can exploit it.

## Patches

The issue has been fixed in n8n versions 1.123.64, 2.29.8, and 2.30.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds

If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict n8n instance access to fully trusted users only.
- Set the `N8N_CONTENT_SECURITY_POLICY` environment variable to a policy that blocks inline scripts.
- Avoid exposing workflows that render externally-controlled input into the HTML node or binary HTML preview to untrusted users.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-p3rg-hrf9-w9gj
- https://nvd.nist.gov/vuln/detail/CVE-2026-65597
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.64
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.29.8
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.30.1
- https://www.vulncheck.com/advisories/n8n-before-dom-based-xss-via-unsandboxed-iframe
