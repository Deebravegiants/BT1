# [M] Next.js has cross-site scripting in beforeInteractive scripts with untrusted input

## Summary
Severity: Medium
Advisory: GHSA-gx5p-jg67-6x7h
CVE: CVE-2026-44580
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-gx5p-jg67-6x7h
Type: github-advisory

## Affected
- npm: `next` — affected >=13.0.0 <15.5.16
- npm: `next` — affected >=16.0.0 <16.2.5

## Details
### Impact

Applications that use `beforeInteractive` scripts together with untrusted content can be vulnerable to cross-site scripting. In affected versions, serialized script content was not escaped safely before being embedded into the document, which could allow attacker-controlled input to break out of the intended script context and execute arbitrary JavaScript in a visitor's browser.

### Fix

We now HTML-escape serialized `beforeInteractive` script content before embedding it into the page, preventing attacker-controlled content from breaking out of the inline script boundary.

### Workarounds

If you cannot upgrade immediately, do not pass untrusted data into `beforeInteractive` scripts. If that pattern is unavoidable, sanitize or escape the content before embedding it.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-gx5p-jg67-6x7h
- https://nvd.nist.gov/vuln/detail/CVE-2026-44580
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v15.5.16
- https://github.com/vercel/next.js/releases/tag/v16.2.5
