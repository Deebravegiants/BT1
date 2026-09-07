# [M] hono Improperly Handles JSX Attribute Names Allows HTML Injection in hono/jsx SSR

## Summary
Severity: Medium
Advisory: GHSA-458j-xx4x-4375
CVE: CVE-2026-56761
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-458j-xx4x-4375
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.14

## Details
## Summary

Improper handling of JSX attribute names in hono/jsx allows malformed attribute keys to corrupt the generated HTML output.

When untrusted input is used as attribute keys during server-side rendering, specially crafted keys can break out of attribute or tag boundaries and inject unintended HTML.

## Details

When rendering JSX elements to HTML strings, attribute values are escaped, but attribute names (keys) were previously inserted into the output without validation.

If an attribute name contains characters such as `"`, `>`, or whitespace, it can alter the structure of the generated HTML.

For example, malformed attribute names can:

* Break out of the current attribute and introduce unintended additional attributes
* Break out of the current HTML tag and inject new elements into the output

This issue arises when untrusted input (such as query parameters or form data) is used as JSX attribute keys during server-side rendering.

## Impact

An attacker who can control attribute keys used in JSX rendering may inject unintended attributes or HTML elements into the generated output.

This may lead to:

* Injection of unexpected HTML attributes
* Corruption of the HTML structure
* Potential cross-site scripting (XSS) if combined with unsafe usage patterns

This issue affects applications that pass untrusted input as JSX attribute keys during server-side rendering.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-458j-xx4x-4375
- https://github.com/honojs/hono
