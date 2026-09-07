# [H] @angular/platform-server: Missing `<noscript>` Raw-Text Serialization Escaping leads to Cross-Site Scripting (XSS) in Angular SSR

## Summary
Severity: High
Advisory: GHSA-gxx4-3xcv-f8qx
CVE: CVE-2026-50556
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-gxx4-3xcv-f8qx
Type: github-advisory

## Affected
- npm: `@angular/platform-server` — affected >=22.0.0-next.0 <22.0.0-rc.2
- npm: `@angular/platform-server` — affected >=21.0.0-next.0 <21.2.16
- npm: `@angular/platform-server` — affected >=20.0.0-next.0 <20.3.24
- npm: `@angular/platform-server` — affected >=19.0.0-next.0 <19.2.25
- npm: `@angular/platform-server` — affected >=0

## Details
A Cross-Site Scripting (XSS) vulnerability exists in `@angular/platform-server`'s DOM emulation dependency (`domino`) when serializing the content of `<noscript>` elements.

When rendering dynamic text content inside a `<noscript>` element via template bindings (such as `{{ value }}` or `[textContent]`), the template engine expects the browser to render the content safely. Under Server-Side Rendering (SSR), `domino` is configured with scripting enabled, meaning `<noscript>` is treated as a raw-text element.

However, `domino`'s serializer completely omitted `<noscript>` from the list of raw-text elements requiring closing-tag escaping during DOM serialization. As a result, any occurrence of `</noscript>` in the bound dynamic text was **never escaped under any circumstances**.

The unescaped closing tag was serialized directly into the output HTML (e.g. `<noscript></noscript><script>alert(1)</script></noscript>`). When parsed by a browser, it closes the `<noscript>` block early, allowing the injected `<script>` block to execute in the user's browser context, causing same-origin Cross-Site Scripting (XSS).

### Impact

This vulnerability allows an attacker to perform same-origin Cross-Site Scripting (XSS) attacks against any user visiting an SSR-rendered page that binds user-controlled data inside a `<noscript>` element. This can lead to session hijacking, credentials theft, unauthorized actions on behalf of users, and defacement.

### Patched Versions

- 22.0.0-rc.2
- 21.2.16
- 20.3.24
- 19.2.25

### Workarounds

If you cannot immediately update your dependencies, you can:

- Avoid binding user-controlled values inside `<noscript>` elements.
- Sanitize any user input placed inside `<noscript>` to explicitly strip closing `</noscript>` tags before passing it to the template.

## References
- https://github.com/angular/angular/security/advisories/GHSA-gxx4-3xcv-f8qx
- https://github.com/angular/angular/issues/68903
- https://github.com/angular/domino/pull/29
- https://github.com/angular/angular
