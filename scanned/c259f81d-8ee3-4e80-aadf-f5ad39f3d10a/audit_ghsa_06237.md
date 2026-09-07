# [M] jsoup: Cleaner may expose markup with custom raw-text elements

## Summary
Severity: Medium
Advisory: GHSA-pmhh-3w7g-xqp8
CVE: CVE-2026-71497
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-pmhh-3w7g-xqp8
Type: github-advisory

## Affected
- Maven: `org.jsoup:jsoup` — affected >=1.14.3 <1.23.1

## Details
When a custom `Safelist` permits certain raw-text elements, jsoup may incorrectly sanitize malformed HTML containing a tag name that ends in a control character. The tag may acquire the parsing behavior of a different element, causing content that should remain text to be emitted as active markup after serialization and potentially allowing XSS.

jsoup’s built-in Safelists are unaffected.

## Patches

Upgrade to jsoup 1.23.1.

## Workarounds

Until upgrading, do not permit raw-text elements in custom Safelists used to clean untrusted HTML.

## Additional security considerations

This fix addresses malformed tag-name handling only.

Permitting raw-text elements in a custom `Safelist` does not make their contents inherently safe. For example, applications that permit `style` must apply appropriate CSS safeguards separately, because jsoup does not parse or sanitize CSS.

## References
- https://github.com/jhy/jsoup/security/advisories/GHSA-pmhh-3w7g-xqp8
- https://github.com/jhy/jsoup/issues/2538
- https://github.com/jhy/jsoup/commit/92f1aca552548b484bc7d4b94c51e48b8e6eca70
- https://github.com/jhy/jsoup
- https://github.com/jhy/jsoup/releases/tag/jsoup-1.23.1
