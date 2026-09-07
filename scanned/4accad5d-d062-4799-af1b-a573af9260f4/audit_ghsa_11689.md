# [M] NotChatbot WebChat has a stored cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w3vx-52j6-9fjp
CVE: CVE-2026-30048
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-w3vx-52j6-9fjp
Type: github-advisory

## Affected
- npm: `@developer.notchatbot/webchat` — affected >=0

## Details
A stored cross-site scripting (XSS) vulnerability exists in the NotChatbot WebChat widget thru 1.4.4. User-supplied input is not properly sanitized before being stored and rendered in the chat conversation history. This allows an attacker to inject arbitrary JavaScript code which is executed when the chat history is reloaded. The issue is reproducible across multiple independent implementations of the widget, indicating that the vulnerability resides in the product itself rather than in a specific website configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-30048
- https://app.unpkg.com/@developer.notchatbot/webchat@1.4.4
- https://gist.github.com/0xN4no/0601f398942a29259d217ea650f694fe
- https://github.com/0xN4no/CVE-2026-30048
- https://www.npmjs.com/package/@developer.notchatbot/webchat
