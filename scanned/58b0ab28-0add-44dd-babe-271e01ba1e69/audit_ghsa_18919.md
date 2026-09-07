# [M] Directus is Vulnerable to Stored Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-vv2v-pw69-8crf
CVE: CVE-2025-64747
CWE: CWE-20, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-11-14
Source: https://github.com/advisories/GHSA-vv2v-pw69-8crf
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <11.13.0

## Details
### Summary

A stored cross-site scripting (XSS) vulnerability exists that allows users with `upload files` and `edit item` permissions to inject malicious JavaScript through the Block Editor interface. Attackers can bypass Content Security Policy (CSP) restrictions by combining file uploads with iframe srcdoc attributes, resulting in persistent XSS execution.

### Details

The vulnerability arises from insufficient sanitization in the Block Editor interface when processing JSON content containing HTML elements. The attack requires two permissions:
- `upload files` - To upload malicious JavaScript files
- `edit item` - To create or modify content with the Block Editor

**Attack Vector:**

1. **JavaScript File Upload**: Attackers upload a malicious JavaScript file via the files endpoint, obtaining a file ID accessible through the assets directory

2. **Block Editor Exploitation**: Using a JSON field with Block Editor interface, attackers inject raw HTML containing an iframe with srcdoc attribute that references the uploaded file

3. **CSP Bypass**: The iframe srcdoc technique circumvents existing CSP protections by creating a new document context that loads the uploaded script

The payload is injected through direct API manipulation (PATCH request) to bypass client-side validation, targeting the Block Editor's paragraph data structure within the JSON content field.

### Impact

This vulnerability enables:
- **Persistent XSS** - Malicious scripts execute whenever affected content is viewed
- **Session hijacking** - Access to authentication tokens and cookies of users viewing the content
- **Administrative compromise** - If administrators view infected content, their elevated privileges can be exploited
- **CSP bypass** - Demonstrates ineffective security controls, potentially affecting other protections
- **Data exfiltration** - Ability to steal sensitive information displayed in the application
- **Phishing attacks** - Injection of convincing fake login forms or malicious redirects

## References
- https://github.com/directus/directus/security/advisories/GHSA-vv2v-pw69-8crf
- https://nvd.nist.gov/vuln/detail/CVE-2025-64747
- https://github.com/directus/directus/commit/d23525317f0780f04aa1fe7a99171a358e43cb2e
- https://github.com/directus/directus
