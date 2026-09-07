# [H] Angular Stored XSS Vulnerability via SVG Animation, SVG URL and MathML Attributes

## Summary
Severity: High
Advisory: GHSA-v4hv-rgfq-gp49
CVE: CVE-2025-66412
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-v4hv-rgfq-gp49
Type: github-advisory

## Affected
- npm: `@angular/compiler` — affected >=21.0.0-next.0 <21.0.2
- npm: `@angular/compiler` — affected >=20.0.0-next.0 <20.3.15
- npm: `@angular/compiler` — affected >=19.0.0-next.0 <19.2.17
- npm: `@angular/compiler` — affected >=0

## Details
A **Stored Cross-Site Scripting ([XSS](https://angular.dev/best-practices/security#preventing-cross-site-scripting-xss))** vulnerability has been identified in the **Angular Template Compiler**. It occurs because the compiler's internal security schema is incomplete, allowing attackers to bypass Angular's built-in security sanitization. Specifically, the schema fails to classify certain URL-holding attributes (e.g., those that could contain [`javascript:` URLs](https://developer.mozilla.org/en-US/Web/URI/Reference/Schemes/javascript)) as requiring strict URL security, enabling the injection of malicious scripts.

Additionally, a related vulnerability exists involving SVG animation elements (`<animate>`, `<set>`, `<animateMotion>`, `<animateTransform>`). The `attributeName` attribute on these elements was not properly validated, allowing attackers to dynamically target security-sensitive attributes like `href` or `xlink:href` on other elements. By binding `attributeName` to "href" and providing a `javascript:` URL in the `values` or `to` attribute, an attacker could bypass sanitization and execute arbitrary code.

Attributes confirmed to be vulnerable include:
*   SVG-related attributes: (e.g., `xlink:href`), and various MathML attributes (e.g., `math|href`, `annotation|href`).
*   SVG animation `attributeName` attribute when bound to "href" or "xlink:href".

When template binding is used to assign untrusted, user-controlled data to these attributes (e.g., `[attr.xlink:href]="maliciousURL"` or `<animate [attributeName]="'href'" [values]="maliciousURL">`), the compiler incorrectly falls back to a non-sanitizing context or fails to block the dangerous attribute assignment. This allows an attacker to inject a `javascript:URL` payload. Upon user interaction (like a click) on the element, or automatically in the case of animations, the malicious JavaScript executes in the context of the application's origin.

### Impact

When exploited, this vulnerability allows an attacker to execute arbitrary code within the context of the vulnerable application's domain. This enables:

* **Session Hijacking:** Stealing session cookies and authentication tokens.  
* **Data Exfiltration:** Capturing and transmitting sensitive user data.  
* **Unauthorized Actions:** Performing actions on behalf of the user.

### Patches

- 19.2.17
- 20.3.15
- 21.0.2

### Attack Preconditions

* The victim's Angular application must render data derived from **untrusted input** (e.g., from a database or API) and bind it to one of the unsanitized URL attributes or the `attributeName` of an SVG animation element.
* The victim must perform a **user interaction** (e.g., clicking) on the compromised element for the stored script to execute, or the animation must trigger the execution.

### Workarounds

If you cannot upgrade, you can workaround the issue by ensuring that any data bound to the vulnerable attributes is never sourced from untrusted user input (e.g., database, API response, URL parameters).

* **Avoid Affected Template Bindings:** Specifically avoid using template bindings (e.g., `[attr.xlink:href]="maliciousURL"`) to assign untrusted data to the vulnerable SVG/MathML attributes.
* **Avoid Dynamic `attributeName` on SVG Animations:** Do not bind untrusted data to the `attributeName` attribute of SVG animation elements (`<animate>`, `<set>`, etc.).
* **Enable [Content Security Policy (CSP)](https://angular.dev/best-practices/security#content-security-policy):** Configure a robust CSP header that disallows `javascript:` URLs.

## References
- https://github.com/angular/angular/security/advisories/GHSA-v4hv-rgfq-gp49
- https://nvd.nist.gov/vuln/detail/CVE-2025-66412
- https://github.com/angular/angular/commit/1c6b0704fb63d051fab8acff84d076abfbc4893a
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://cert-portal.siemens.com/productcert/html/ssa-485750.html
- https://github.com/angular/angular
