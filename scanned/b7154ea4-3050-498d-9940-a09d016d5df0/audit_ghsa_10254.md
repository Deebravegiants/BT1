# [M] DOMPurify USE_PROFILES prototype pollution allows event handlers

## Summary
Severity: Medium
Advisory: GHSA-cj63-jhhr-wcxv
CVE: CVE-2026-65913
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-cj63-jhhr-wcxv
Type: github-advisory

## Affected
- npm: `dompurify` — affected >=0 <3.3.2

## Details
## Summary
When `USE_PROFILES` is enabled, DOMPurify rebuilds `ALLOWED_ATTR` as a plain array before populating it with the requested allowlists. Because the sanitizer still looks up attributes via `ALLOWED_ATTR[lcName]`, any `Array.prototype` property that is polluted also counts as an allowlisted attribute. An attacker who can set `Array.prototype.onclick = true` (or a runtime already subject to prototype pollution) can thus force DOMPurify to keep event handlers such as `onclick` even when they are normally forbidden. The provided PoC sanitizes `<img onclick=...>` with `USE_PROFILES` and adds the sanitized output to the DOM; the polluted prototype allows the event handler to survive and execute, turning what should be a blocklist into a silent XSS vector.

## Impact
Prototype pollution makes DOMPurify accept dangerous event handler attributes, which bypasses the sanitizer and results in DOM-based XSS once the sanitized markup is rendered.

## Credits
Identified by Cantina’s Apex (https://www.cantina.security).

## References
- https://github.com/cure53/DOMPurify/security/advisories/GHSA-cj63-jhhr-wcxv
- https://github.com/cure53/DOMPurify
- https://github.com/cure53/DOMPurify/releases/tag/3.3.2
