# [M] n8n Vulnerable to XSS via Binary Data Inline HTML Rendering

## Summary
Severity: Medium
Advisory: GHSA-qfc3-hm4j-7q77
CVE: CVE-2026-33749
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-qfc3-hm4j-7q77
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.27
- npm: `n8n` — affected >=2.14.0 <2.14.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.13.3

## Details
## Impact
An authenticated user with permission to create or modify workflows could craft a workflow that produces an HTML binary data object without a filename. The `/rest/binary-data` endpoint served such responses inline on the n8n origin without `Content-Disposition` or `Content-Security-Policy` headers, allowing the HTML to render in the browser with full same-origin JavaScript access.

By sending the resulting URL to a higher-privileged user, an attacker could execute JavaScript in the victim's authenticated session, enabling exfiltration of workflows and credentials, modification of workflows, or privilege escalation to admin.

## Patches
The issue has been fixed in n8n versions 1.123.27, 2.13.3, and 2.14.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Restrict network access to the n8n instance to prevent untrusted users from accessing binary data URLs.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-qfc3-hm4j-7q77
- https://nvd.nist.gov/vuln/detail/CVE-2026-33749
- https://github.com/n8n-io/n8n
