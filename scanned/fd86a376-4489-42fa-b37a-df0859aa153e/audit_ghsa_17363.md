# [H] n8n's Possible Stored XSS in "Respond to Webhook" Node May Execute Outside iframe Sandbox

## Summary
Severity: High
Advisory: GHSA-58jc-rcg5-95f3
CVE: CVE-2025-61914
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-12-26
Source: https://github.com/advisories/GHSA-58jc-rcg5-95f3
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.114.0

## Details
### Summary
A stored Cross-Site Scripting (XSS) vulnerability may occur in n8n when using the “Respond to Webhook” node.
When this node responds with HTML content containing executable scripts, the payload may execute directly in the top-level window, rather than within the expected sandbox introduced in version 1.103.0.

This behavior can enable a malicious actor with workflow creation permissions to execute arbitrary JavaScript in the context of the n8n editor interface.

While session cookies (`n8n-auth`) are marked `HttpOnly` and cannot be directly exfiltrated, the vulnerability can facilitate Cross-Site Request Forgery (CSRF)-like actions from within the user’s authenticated session, potentially allowing:

- Unauthorized reading of sensitive workflow data or execution history.
- Unauthorized modification or deletion of workflows.
- Insertion of malicious workflow logic or external data exfiltration steps.

n8n instances that allow untrusted users to create workflows are particularly impacted.

### Patches
The vulnerability has been patched in v.1.114.0.

### Workarounds
- Restrict workflow creation and modification privileges to trusted users only.
- Avoid using untrusted HTML responses in the “Respond to Webhook” node.
- Use an external reverse proxy or HTML sanitizer to filter responses that include executable scripts.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-58jc-rcg5-95f3
- https://nvd.nist.gov/vuln/detail/CVE-2025-61914
- https://github.com/n8n-io/n8n
