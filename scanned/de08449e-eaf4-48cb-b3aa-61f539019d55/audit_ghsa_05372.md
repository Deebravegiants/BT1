# [H] html2pdf.js contains a cross-site scripting vulnerability

## Summary
Severity: High
Advisory: GHSA-w8x4-x68c-m6fc
CVE: CVE-2026-22787
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-14
Source: https://github.com/advisories/GHSA-w8x4-x68c-m6fc
Type: github-advisory

## Affected
- npm: `html2pdf.js` — affected >=0 <0.14.0

## Details
### Impact
html2pdf.js contains a cross-site scripting (XSS) vulnerability when given a text source rather than an element. This text is not sufficiently sanitized before being attached to the DOM, allowing malicious scripts to be run on the client browser and risking the confidentiality, integrity, and availability of the page's data.

Example attack vector:

```js
import html2pdf from 'html2pdf.js/src/index.js';

const maliciousHTML = '<img src=x onerror="alert(document.cookie)">';
html2pdf(maliciousHTML);
// or html2pdf().from(maliciousHTML);
```

### Patches
This vulnerability has been fixed in html2pdf.js@0.14.0 to sanitize text sources using DOMPurify. There are no other breaking changes in this version.

### Workarounds
Users of earlier versions of html2pdf.js must safely sanitize any text before using it as a source in html2pdf.js.

### References
- Initial report: https://github.com/eKoopmans/html2pdf.js/issues/865
- Fix: https://github.com/eKoopmans/html2pdf.js/pull/877, [v0.14.0](https://github.com/eKoopmans/html2pdf.js/releases/tag/v0.14.0)
- CVE-2026-22787: https://nvd.nist.gov/vuln/detail/CVE-2026-22787

## References
- https://github.com/eKoopmans/html2pdf.js/security/advisories/GHSA-w8x4-x68c-m6fc
- https://nvd.nist.gov/vuln/detail/CVE-2026-22787
- https://github.com/eKoopmans/html2pdf.js/issues/865
- https://github.com/eKoopmans/html2pdf.js/pull/877
- https://github.com/eKoopmans/html2pdf.js/commit/988826e336035b39a8608182d7b73c0e3cd78c7b
- https://aydinnyunus.github.io/2026/01/17/cve-2026-22787-html2pdf-xss-vulnerability
- https://github.com/eKoopmans/html2pdf.js
- https://github.com/eKoopmans/html2pdf.js/releases/tag/v0.14.0
