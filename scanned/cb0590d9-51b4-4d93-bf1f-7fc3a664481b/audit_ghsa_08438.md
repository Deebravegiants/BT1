# [H] NukeViet CMS: Stored Cross-Site Scripting (XSS) via insufficient server-side input sanitization in Request class

## Summary
Severity: High
Advisory: GHSA-64rr-pp78-62ww
CVE: CVE-2026-41147
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-64rr-pp78-62ww
Type: github-advisory

## Affected
- Packagist: `nukeviet/nukeviet` — affected >=0

## Details
### Impact

NukeViet CMS <= 4.5.08 contains a Stored Cross-Site Scripting (XSS) vulnerability caused by insufficient server-side input sanitization in the Request class. The application relies primarily on client-side filtering to sanitize HTML tags and attributes in user-submitted content, which can be bypassed by intercepting and modifying HTTP requests directly (e.g., using Burp Suite).

This affects any module or functionality that accepts user HTML input through the Request class. An attacker can inject malicious payloads such as `<iframe srcdoc="&lt;img src=1 onerror=alert(document.cookie)&gt;"></iframe>`, which are stored server-side and executed in the browser of any user who views the content.

**Who is impacted:**
- Administrators and moderators who view user-submitted content (e.g., contact messages, comments, or any module using the Request class for HTML input).
- The Contact module was used as a proof of concept, but the vulnerability is not limited to this module.
- No authentication is required to exploit this vulnerability, making it accessible to any anonymous visitor.

**Potential impact includes:**
- Session hijacking via cookie theft (for non-HttpOnly cookies)
- Performing actions on the application under the victim's identity
- Defacement or redirection to phishing pages
- Phishing attacks via manipulated email notifications

### Patches

This vulnerability has been fixed in NukeViet 4.5.08. Users should upgrade to version >= 4.5.08.

### Workarounds

- Implement server-side HTML sanitization in the Request class to strip or encode dangerous tags and attributes (e.g., `<iframe>`, `srcdoc`, event handlers such as `onerror`, `onload`).
- Apply a Content Security Policy (CSP) header to restrict inline script execution.
- Ensure cookies are set with the `HttpOnly` flag to mitigate cookie theft via XSS.

### Resources

- Affected source: https://github.com/nukeviet/nukeviet/blob/nukeviet4.5/modules/contact/funcs/main.php
- CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting'): https://cwe.mitre.org/data/definitions/79.html

## References
- https://github.com/nukeviet/nukeviet/security/advisories/GHSA-64rr-pp78-62ww
- https://nvd.nist.gov/vuln/detail/CVE-2026-41147
- https://github.com/nukeviet/nukeviet/commit/2a0860fbe22e2f6a3b90f802bf80b25e18699611
- https://github.com/nukeviet/nukeviet
- https://github.com/nukeviet/nukeviet/releases/tag/4.5.08
