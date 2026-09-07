# [M] DOMPurify ADD_ATTR predicate skips URI validation

## Summary
Severity: Medium
Advisory: GHSA-cjmm-f4jc-qw8r
CVE: CVE-2026-65912
CWE: CWE-183
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-cjmm-f4jc-qw8r
Type: github-advisory

## Affected
- npm: `dompurify` — affected >=0 <3.3.2

## Details
## Summary
DOMPurify allows `ADD_ATTR` to be provided as a predicate function via `EXTRA_ELEMENT_HANDLING.attributeCheck`. When the predicate returns `true`, `_isValidAttribute` short-circuits the attribute check before URI-safe validation runs. An attacker who supplies a predicate that accepts specific attribute/tag combinations can then sanitize input such as `<a href="javascript:alert(document.domain)">` and have the `javascript:` URL survive, because URI validation is skipped for that attribute while other checks still pass. The provided PoC accepts `href` for anchors and then triggers a click inside an iframe, showing that the sanitized payload executes despite the protocol bypass.

## Impact
Predicate-based allowlisting bypasses DOMPurify's URI validation, allowing unsafe protocols such as `javascript:` to reach the DOM and execute whenever the link is activated, resulting in DOM-based XSS.

## Credits
Identified by Cantina’s Apex (https://www.cantina.security).

## References
- https://github.com/cure53/DOMPurify/security/advisories/GHSA-cjmm-f4jc-qw8r
- https://github.com/cure53/DOMPurify
- https://github.com/cure53/DOMPurify/releases/tag/3.3.2
