# [M] Hostname spoofing via backslashes in URL

## Summary
Severity: Medium
Advisory: GHSA-3329-pjwv-fjpg
CVE: CVE-2020-26291
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-12-30
Source: https://github.com/advisories/GHSA-3329-pjwv-fjpg
Type: github-advisory

## Affected
- npm: `urijs` — affected >=0 <1.19.4

## Details
### Impact
If using affected versions to determine a URL's hostname, the hostname can be spoofed by using a backslash (`\`) character followed by an at (`@`) character. If the hostname is used in security decisions, the decision may be incorrect.

Depending on library usage and attacker intent, impacts may include allow/block list bypasses, SSRF attacks, open redirects, or other undesired behavior.

Example URL: `https://expected-example.com\@observed-example.com`
Escaped string: `https://expected-example.com\\@observed-example.com` (JavaScript strings must escape backslash)

Affected versions incorrectly return `observed-example.com`. Patched versions correctly return `expected-example.com`. Patched versions match the behavior of other parsers which implement the [WHATWG URL specification](https://url.spec.whatwg.org/), including web browsers and [Node's built-in URL class](https://nodejs.org/api/url.html).

### Patches
Version 1.19.4 is patched against all known payload variants. Version 1.19.3 has a partial patch but is still vulnerable to a payload variant.

### References
https://github.com/medialize/URI.js/releases/tag/v1.19.4 (complete fix for this bypass)
https://github.com/medialize/URI.js/releases/tag/v1.19.3 (partial fix for this bypass)
[PR #233](https://github.com/medialize/URI.js/pull/233) (initial fix for backslash handling)

### For more information
If you have any questions or comments about this advisory, open an issue in https://github.com/medialize/URI.js

### Reporter credit
[Alesandro Ortiz](https://AlesandroOrtiz.com)

## References
- https://github.com/medialize/URI.js/security/advisories/GHSA-3329-pjwv-fjpg
- https://nvd.nist.gov/vuln/detail/CVE-2020-26291
- https://github.com/medialize/URI.js/commit/b02bf037c99ac9316b77ff8bfd840e90becf1155
- https://github.com/medialize/URI.js
- https://github.com/medialize/URI.js/releases/tag/v1.19.4
- https://www.npmjs.com/advisories/1595
- https://www.npmjs.com/package/urijs
