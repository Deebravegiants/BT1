# [M] @angular/compiler: Two-Way Property Binding Sanitization Bypass (XSS)

## Summary
Severity: Medium
Advisory: GHSA-58w9-8g37-x9v5
CVE: CVE-2026-54265
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-58w9-8g37-x9v5
Type: github-advisory

## Affected
- npm: `@angular/compiler` — affected >=22.0.0-next.0 <22.0.1
- npm: `@angular/compiler` — affected >=21.0.0-next.0 <21.2.17
- npm: `@angular/compiler` — affected >=20.0.0-next.0 <20.3.25
- npm: `@angular/compiler` — affected >=0

## Details
An issue in the `@angular/compiler` package allows bypassing DOM property sanitization through the use of two-way property bindings.

Specifically, when a native DOM property that requires sanitization (such as `innerHTML`, `srcdoc`, `src`, `href`, `data`, or `sandbox`) is bound using the two-way binding syntax (e.g., `[(innerHTML)]="value"` or `bindon-innerHTML="value"`), the Angular template compiler failed to apply the appropriate schema-derived sanitizer resolution to the `TwoWayProperty` operation. As a result, native two-way DOM bindings were emitted without the required sanitizer function, whereas equivalent one-way bindings would be properly sanitized.

This flaw enables an attacker who can control the value of a two-way bound sensitive property to bypass Angular's built-in sanitization logic, potentially leading to client-side Cross-Site Scripting (XSS).

### Impact
Any Angular application that uses two-way data binding (`[()]` or `bindon-`) on security-sensitive native DOM properties (like `innerHTML`, `href` on `<a>`, `src` on `<img>`/`<iframe>`, etc.) is vulnerable to this security bypass.

Once exploited, this allows a malicious actor to supply an unsanitized property binding value that bypasses core sanitization constraints. This could lead to the execution of arbitrary JavaScript within the target user's browser context, potentially resulting in session hijacking, sensitive data exposure, or unauthorized actions on behalf of the user.

### Attack Preconditions
To successfully exploit this vulnerability, the following environment parameters and application states must concurrently exist:
1. **Two-Way Binding on Sensitive Properties:** The application must bind to a sensitive native DOM property using the two-way binding syntax (e.g., `<div [(innerHTML)]="userContent"></div>`).
2. **User-Controlled Input:** The value bound to this property must be influenceable by user-controlled input.
3. **Absence of Additional Sanitization:** The application does not perform separate manual sanitization (e.g., via `DomSanitizer`) before passing the value to the bound property.

### Patches
* 22.0.1
* 21.2.17
* 20.3.25

## References
- https://github.com/angular/angular/security/advisories/GHSA-58w9-8g37-x9v5
- https://nvd.nist.gov/vuln/detail/CVE-2026-54265
- https://github.com/angular/angular/pull/69107
- https://github.com/angular/angular/commit/3c70270c96677c0dd33585f2afe8e187113e5fb4
- https://github.com/angular/angular
