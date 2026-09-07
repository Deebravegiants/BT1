# [M] DOMPurify IN_PLACE Sanitization Bypass via Attached Shadow Root Inside <template>.content

## Summary
Severity: Medium
Advisory: GHSA-rp9w-3fw7-7cwq
CVE: CVE-2026-49978
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-rp9w-3fw7-7cwq
Type: github-advisory

## Affected
- npm: `dompurify` — affected >=0 <3.4.7

## Details
If the HTML you give it contains a <template> element, and inside that template there's an element with a shadow DOM attached to it, DOMPurify quietly skips over the shadow contents. Whatever the attacker put in there - an image with an onerror handler, a link with a javascript: URL, even a full script - survives untouched. The moment the application uses that template the way templates are meant to be used (cloning it and inserting the result into the page), the malicious payload comes along and runs as if it had never been sanitized. From there an attacker gets everything XSS normally gets them: session cookies, stored tokens, the ability to act as the user, and the ability to leave persistent payloads behind for the next person who visits.

[advisory.pdf](https://github.com/user-attachments/files/28275600/advisory.pdf)

[poc.html](https://github.com/user-attachments/files/28275708/poc.html)

## References
- https://github.com/cure53/DOMPurify/security/advisories/GHSA-rp9w-3fw7-7cwq
- https://github.com/cure53/DOMPurify
