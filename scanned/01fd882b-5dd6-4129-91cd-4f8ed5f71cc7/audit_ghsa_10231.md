# [M] justhtml has sanitization bypass in custom policies and programmatic DOM

## Summary
Severity: Medium
Advisory: GHSA-vrx2-77f2-ww34
CWE: CWE-436, CWE-471, CWE-79, CWE-835
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-vrx2-77f2-ww34
Type: github-advisory

## Affected
- PyPI: `justhtml` — affected >=0 <1.17.0

## Details
## Summary

`justhtml` `1.17.0` fixes multiple security issues in sanitization, serialization, and programmatic DOM handling.

Most of these issues affected advanced or custom configurations rather than the default safe path.

## Affected versions

- `justhtml` `<= 1.16.0`

## Fixed version

- `justhtml` `1.17.0` released on April 19, 2026

## Impact

### Custom SVG / MathML sanitization policies
Custom policies that preserved foreign namespaces could allow dangerous content to survive sanitization, including:

- active HTML integration points such as SVG `<foreignObject>`, MathML `<annotation-xml encoding="text/html">`, SVG `<title>` / `<desc>`, and MathML text integration points
- mutation-XSS parser-differential payloads that looked inert in memory but became active HTML after reparse
- SVG `filter="url(...)"` attributes that could trigger external fetches

These issues affected:
- `JustHTML(..., sanitize=True)` with custom foreign-namespace policies
- `sanitize()` / `sanitize_dom()`
- low-level terminal `Sanitize(...)` transform execution

### Preserved `<style>` handling
Constructor-time sanitization and explicit `Sanitize(...)` transforms did not fully match `sanitize()` / `sanitize_dom()` when custom policies preserved `<style>`.

That could leave resource-loading CSS such as `@import` or `background-image:url(...)` in sanitized output from HTML string input.

### Programmatic DOM serialization
Programmatic `script`, `style`, and `Comment(...)` nodes could still serialize into active markup in some edge cases.

This could affect applications that build or mutate DOM trees directly before calling `to_html()` or `to_markdown(html_passthrough=True)`.

### Cache mutation and DOM cycle handling
Two lower-severity hardening fixes were included:

- compiled sanitize-pipeline caches could be mutated after warming and weaken later sanitization
- parent/child cycles in programmatic DOM trees could cause infinite loops in operations such as `to_html()` and `sanitize_dom()`

## Default configuration

Most of the issues above did **not** affect ordinary parsed HTML with the default `JustHTML(..., sanitize=True)` configuration.

The main risk areas were:

- custom policies that preserve SVG or MathML
- custom policies that preserve `<style>`
- programmatic DOM construction or mutation
- low-level direct sanitizer/transform APIs

## Recommended action

Upgrade to `justhtml` `1.17.0`.

If users cannot upgrade immediately:

- avoid preserving SVG or MathML for untrusted input
- avoid preserving `<style>` for untrusted input
- avoid mutating programmatic DOM trees with untrusted `script`, `style`, or comment content
- avoid mutating warmed policy internals or sanitizer caches

## Credit

Discovered during an internal security review of `justhtml`.

## References
- https://github.com/EmilStenstrom/justhtml/security/advisories/GHSA-vrx2-77f2-ww34
- https://github.com/EmilStenstrom/justhtml
