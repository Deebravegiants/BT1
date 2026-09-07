# [M] n8n has a Stored XSS Vulnerability in its Form Trigger

## Summary
Severity: Medium
Advisory: GHSA-q4fm-pjq6-m63g
CVE: CVE-2026-56358
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-q4fm-pjq6-m63g
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.0.0-rc.0 <2.11.2
- npm: `n8n` — affected >=0 <1.123.25

## Details
## Impact
An authenticated user with permission to create or modify workflows could exploit a flaw in the Form Trigger node's CSS sanitization to store a cross-site scripting (XSS) payload. The injected script executes persistently for every visitor of the published form, enabling form submission hijacking and phishing. The existing Content Security Policy prevents direct n8n session cookie theft but does not prevent script execution or form action manipulation.

## Patches
The issue has been fixed in n8n versions 2.12.0, 2.11.2, and 1.123.25. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the Form Trigger node by adding `n8n-nodes-base.formTrigger` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-q4fm-pjq6-m63g
- https://nvd.nist.gov/vuln/detail/CVE-2026-56358
- https://github.com/n8n-io/n8n
- https://www.vulncheck.com/advisories/n8n-stored-cross-site-scripting-in-form-trigger-node
