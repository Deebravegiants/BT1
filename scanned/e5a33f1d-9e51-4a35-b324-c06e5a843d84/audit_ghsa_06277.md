# [H] Angular SSR: Missing Fallback Raw-Content Serialization Escaping leads to Cross-Site Scripting (XSS)

## Summary
Severity: High
Advisory: GHSA-vpx6-8pjr-4g3v
CVE: CVE-2026-69149
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-vpx6-8pjr-4g3v
Type: github-advisory

## Affected
- npm: `@angular/platform-server` — affected >=22.0.0-next.0 <22.0.7
- npm: `@angular/platform-server` — affected >=21.0.0-next.0 <21.2.19
- npm: `@angular/platform-server` — affected >=20.0.0-next.0 <20.3.27
- npm: `@angular/platform-server` — affected >=0

## Details
A Cross-Site Scripting (XSS) vulnerability exists in `@angular/platform-server`'s DOM emulation dependency (`domino`) when serializing the content of fallback raw-content elements (`<iframe>`, `<noembed>`, `<noframes>`, and `<noscript>`).

When rendering dynamic text content inside fallback raw-content elements via template bindings, the template engine expects the browser to render the content safely. Under Server-Side Rendering (SSR), `domino` is configured with scripting enabled, meaning these elements are treated as raw-text elements.

However, `domino`'s serializer previously did not escape text nodes within fallback raw-content elements (`<iframe>`, `<noembed>`, `<noframes>`, `<noscript>`) during DOM serialization. As a result, any occurrence of closing tags in the bound dynamic text was not escaped.

The unescaped closing tag could be serialized directly into the output HTML. When parsed by a browser or re-parsed during SSR post-processing without preserving raw-content parser state, an injected closing tag closes the element early, allowing an injected script block to execute in the user's browser context, causing same-origin Cross-Site Scripting (XSS).

### Impact

This vulnerability allows an attacker to perform same-origin Cross-Site Scripting (XSS) attacks against any user visiting an SSR-rendered page that binds user-controlled data inside fallback raw-content elements (`<iframe>`, `<noembed>`, `<noframes>`, `<noscript>`). This can lead to session hijacking, credentials theft, unauthorized actions on behalf of users, and defacement.

### Patched Versions

- 22.0.7
- 21.2.19
- 20.3.27

### Workarounds
If you cannot immediately update your dependencies, you can mitigate this issue using any of the following approaches:
- **Disable critical CSS inlining**: Critical CSS inlining in Angular SSR post-processes the rendered HTML using `domino`. Disabling this step prevents `domino` from re-parsing and re-serializing the HTML during server-side rendering.
  - In `angular.json`, set `inlineCritical` to `false` under style optimization options:
    ```json
    {
      "projects": {
        "my-app": {
          "architect": {
            "build": {
              "builder": "@angular/build:application",
              "options": {
                "optimization": {
                  "styles": {
                    "inlineCritical": false
                  }
                }
              }
            }
          }
        }
      }
    }
    ```
  - When rendering programmatically with `CommonEngine`, set `inlineCriticalCss: false` in your render options.
- **Avoid binding user-controlled values** inside fallback raw-content elements (`<iframe>`, `<noembed>`, `<noframes>`, `<noscript>`).
- **Sanitize user input** placed inside these elements to explicitly strip or escape closing tags before passing it to the template.

## References
- https://github.com/angular/angular/security/advisories/GHSA-vpx6-8pjr-4g3v
- https://github.com/angular/angular/pull/69675
- https://github.com/angular/angular/pull/69714
- https://github.com/angular/angular/pull/69929
- https://github.com/angular/angular/pull/69930
- https://github.com/angular/domino/pull/32
- https://github.com/angular/domino/commit/f88e5aa49cf2804d7c2df22ef1640eb4ec43dd56
- https://github.com/angular/angular
