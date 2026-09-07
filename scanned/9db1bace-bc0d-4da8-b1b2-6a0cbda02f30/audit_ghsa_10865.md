# [H] Angular vulnerable to XSS in i18n attribute bindings

## Summary
Severity: High
Advisory: GHSA-g93w-mfhg-p222
CVE: CVE-2026-32635
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-g93w-mfhg-p222
Type: github-advisory

## Affected
- npm: `@angular/core` — affected >=22.0.0-next.0 <22.0.0-next.3
- npm: `@angular/core` — affected >=21.0.0-next.0 <21.2.4
- npm: `@angular/core` — affected >=20.0.0-next.0.0.0 <20.3.18
- npm: `@angular/core` — affected >=19.0.0-next.0 <19.2.20
- npm: `@angular/core` — affected >=17.0.0-next.0
- npm: `@angular/compiler` — affected >=22.0.0-next.0 <22.0.0-next.3
- npm: `@angular/compiler` — affected >=21.0.0-next.0 <21.2.4
- npm: `@angular/compiler` — affected >=20.0.0-next.0.0.0 <20.3.18
- npm: `@angular/compiler` — affected >=19.0.0-next.0 <19.2.20
- npm: `@angular/compiler` — affected >=17.0.0-next.0

## Details
A Cross-Site Scripting (XSS) vulnerability has been identified in the Angular runtime and compiler. It occurs when the application uses a security-sensitive attribute (for example href on an anchor tag) together with Angular's ability to internationalize attributes. Enabling internationalization for the sensitive attribute by adding `i18n-<attribute>` name bypasses Angular's built-in sanitization mechanism, which when combined with a data binding to untrusted user-generated data can allow an attacker to inject a malicious script. 

The following example illustrates the issue:
```html
<a href="{{maliciousUrl}}" i18n-href>Click me</a>
```

The following attributes have been confirmed to be vulnerable:
- `action`
- `background`
- `cite`
- `codebase`
- `data`
- `formaction`
- `href`
- `itemtype`
- `longdesc`
- `poster`
- `src`
- `xlink:href`

### Impact
When exploited, this vulnerability allows an attacker to execute arbitrary code within the context of the vulnerable application's domain. This enables:
- Session Hijacking: Stealing session cookies and authentication tokens.
- Data Exfiltration: Capturing and transmitting sensitive user data.
- Unauthorized Actions: Performing actions on behalf of the user.

### Attack Preconditions
1. The application must use a vulnerable version of Angular.
2. The application must bind unsanitized user input to one of the attributes mentioned above.
3. The bound value must be marked for internationalization via the presence of a `i18n-<name>` attribute on the same element.

### Patches
- 22.0.0-next.3
- 21.2.4
- 20.3.18
- 19.2.20

### Workarounds
The primary workaround is to ensure that any data bound to the vulnerable attributes is **never sourced from untrusted user input** (e.g., database, API response, URL parameters) until the patch is applied, or when it is, it shouldn't be marked for internationalization.

Alternatively, users can explicitly sanitize their attributes by passing them through Angular's `DomSanitizer`:
```ts
import {Component, inject, SecurityContext} from '@angular/core';
import {DomSanitizer} from '@angular/platform-browser';

@Component({
  template: `
    <form action="{{url}}" i18n-action>
      <button>Submit</button>
    </form>
  `,
})
export class App {
  url: string;

  constructor() {
    const dangerousUrl = 'javascript:alert(1)';
    const sanitizer = inject(DomSanitizer);
    this.url = sanitizer.sanitize(SecurityContext.URL, dangerousUrl) || '';
  }
}
```

### References
- [Fix 1](https://github.com/angular/angular/pull/67541) 
- [Fix 2](https://github.com/angular/angular/pull/67561)

## References
- https://github.com/angular/angular/security/advisories/GHSA-g93w-mfhg-p222
- https://nvd.nist.gov/vuln/detail/CVE-2026-32635
- https://github.com/angular/angular/pull/67541
- https://github.com/angular/angular/pull/67561
- https://github.com/angular/angular/commit/224e60ecb1b90115baa702f1c06edc1d64d86187
- https://github.com/angular/angular/commit/78dea55351fb305b33a919c43a6b363137eca166
- https://github.com/angular/angular/commit/8630319f74c9575a21693d875cc7d5252516146d
- https://github.com/angular/angular/commit/ed2d324f9cc12aab6cfa0569ef10b73243a62c65
- https://github.com/angular/angular
