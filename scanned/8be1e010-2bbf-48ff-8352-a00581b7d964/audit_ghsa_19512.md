# [M] n8n Vulnerable to Stored XSS through Attachments View Endpoint

## Summary
Severity: Medium
Advisory: GHSA-c8hm-hr8h-5xjw
CVE: CVE-2025-46343
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-04-28
Source: https://github.com/advisories/GHSA-c8hm-hr8h-5xjw
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.90.0

## Details
### Impact
n8n workflows can store and serve binary files, which are accessible to authenticated users. However, there was no restriction on the MIME type of uploaded files, and the MIME type could be controlled via a GET parameter. This allowed the server to respond with any MIME type, potentially enabling malicious content to be interpreted and executed by the browser.

An authenticated attacker with member-level permissions could exploit this by uploading a crafted HTML file containing malicious JavaScript. When another user visits the binary data endpoint with the MIME type set to text/html, the script executes in the context of the user’s session. This script could, for example, send a request to change the user’s email address in their account settings, effectively enabling account takeover.

### Patches

- [n8n@1.90.0](https://github.com/n8n-io/n8n/releases/tag/n8n%401.90.0)

### Credit
We would like to thank @Mahmoud0x00 for reporting this issue.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-c8hm-hr8h-5xjw
- https://nvd.nist.gov/vuln/detail/CVE-2025-46343
- https://github.com/n8n-io/n8n/pull/14350
- https://github.com/n8n-io/n8n/pull/14685
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n%401.90.0
