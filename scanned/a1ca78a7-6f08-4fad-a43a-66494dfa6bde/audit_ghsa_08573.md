# [M] hono/jsx has Unvalidated JSX Tag Names that May Allow HTML Injection

## Summary
Severity: Medium
Advisory: GHSA-69xw-7hcm-h432
CVE: CVE-2026-44455
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-69xw-7hcm-h432
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.16

## Details
## Summary

Improper handling of JSX element tag names in hono/jsx allowed unvalidated tag names to be directly inserted into the generated HTML output.

When untrusted input is used as a tag name via the programmatic `jsx()` or `createElement()` APIs during server-side rendering, specially crafted values may break out of the intended element context and inject unintended HTML.

## Details

When rendering JSX elements to HTML strings, attribute values are escaped and attribute names are validated. However, element tag names were previously inserted into the output without validation.

If a tag name contains characters such as `<`, `>`, quotes, or whitespace, it may alter the structure of the generated HTML.

For example, malformed tag names can:

* Break out of the intended element and introduce unintended HTML elements
* Inject attributes or event handlers into the rendered output

This issue arises when untrusted input (such as query parameters or database content) is used as JSX tag names via `jsx()` or `createElement()` during server-side rendering.

## Impact

An attacker who can control tag names used in JSX rendering may inject unintended HTML into the generated output.

This may lead to:

* Injection of unexpected HTML elements or attributes
* Corruption of the HTML structure
* Cross-site scripting (XSS) when combined with unsafe usage patterns

This issue only affects applications that construct JSX tag names from untrusted input. Applications using static or allowlisted tag names are not affected.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-69xw-7hcm-h432
- https://nvd.nist.gov/vuln/detail/CVE-2026-44455
- https://github.com/honojs/hono
