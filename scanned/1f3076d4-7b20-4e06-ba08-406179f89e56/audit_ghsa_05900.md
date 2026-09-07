# [H] Angular i18n: Cross-Site Scripting (XSS) via event-handler attributes

## Summary
Severity: High
Advisory: GHSA-jj27-h5hq-8x99
CVE: CVE-2026-69151
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-jj27-h5hq-8x99
Type: github-advisory

## Affected
- npm: `@angular/compiler` — affected >=22.0.0-next.0 <22.0.1
- npm: `@angular/compiler` — affected >=21.0.0-next.0 <21.2.19
- npm: `@angular/compiler` — affected >=20.0.0-next.0 <20.3.27
- npm: `@angular/compiler` — affected >=0
- npm: `@angular/core` — affected >=22.0.0-next.0 <22.0.1
- npm: `@angular/core` — affected >=21.0.0-next.0 <21.2.19
- npm: `@angular/core` — affected >=20.0.0-next.0 <20.3.27
- npm: `@angular/core` — affected >=0

## Details
A Cross-Site Scripting (XSS) vulnerability has been identified in the Angular compiler's internationalization (i18n) pipeline. Although Angular disallows binding to event-handler attributes such as `onclick` and `onerror` through standard attribute validation (`validateAttribute()` / `validateProperty()`), the i18n metadata collection path allowed these same attribute names to be marked for translation using `i18n-on*` attributes (e.g., `i18n-onerror`).

When exploited, a lower-trust translation file could replace a benign static handler such as `onerror="void 0"` with arbitrary executable JavaScript in the localized build.

The following example illustrates a vulnerable pattern:
```html
<img src="foo.jpg" onerror="void 0" i18n-onerror />
```

### Impact

When exploited, this vulnerability allows arbitrary JavaScript execution within the context of the vulnerable application's domain if an attacker can control or influence the translation files used during localization. This can lead to:
- **Session Hijacking**: Accessing session cookies, tokens, or sensitive user data.
- **Unauthorized Actions**: Performing actions on behalf of the authenticated user.

### Patched Versions

- 22.0.1
- 21.2.19
- 20.3.27

### Workarounds

Ensure that static event-handler attributes (e.g., `onerror`, `onclick`) are never marked for internationalization (`i18n-on*`) in application templates, and ensure translation files are sourced from trusted origins.

## References
- https://github.com/angular/angular/security/advisories/GHSA-jj27-h5hq-8x99
- https://github.com/angular/angular/pull/68821
- https://github.com/angular/angular/pull/69306
- https://github.com/angular/angular/commit/417a4071a776464d549509ed3aec121dbd2fda5e
- https://github.com/angular/angular/commit/6c41f5ca01c0ae045fc7d929b72853a11eb55865
- https://github.com/angular/angular
