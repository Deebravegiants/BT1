# [H] Angular has XSS Vulnerability via Unsanitized SVG Script Attributes

## Summary
Severity: High
Advisory: GHSA-jrmj-c5cx-3cw6
CVE: CVE-2026-22610
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-09
Source: https://github.com/advisories/GHSA-jrmj-c5cx-3cw6
Type: github-advisory

## Affected
- npm: `@angular/compiler` — affected >=21.1.0-next.0 <21.1.0-rc.0
- npm: `@angular/core` — affected >=21.1.0-next.0 <21.1.0-rc.0
- npm: `@angular/compiler` — affected >=21.0.0-next.0 <21.0.7
- npm: `@angular/core` — affected >=21.0.0-next.0 <21.0.7
- npm: `@angular/compiler` — affected >=20.0.0-next.0 <20.3.16
- npm: `@angular/core` — affected >=20.0.0-next.0 <20.3.16
- npm: `@angular/compiler` — affected >=19.0.0-next.0 <19.2.18
- npm: `@angular/core` — affected >=19.0.0-next.0 <19.2.18
- npm: `@angular/compiler` — affected >=0
- npm: `@angular/core` — affected >=0

## Details
A Cross-Site Scripting (XSS) vulnerability has been identified in the Angular Template Compiler. The vulnerability exists because Angular’s internal sanitization schema fails to recognize the `href` and `xlink:href` attributes of SVG `<script>` elements as a **Resource URL** context.

In a standard security model, attributes that can load and execute code (like a script's source) should be strictly validated. However, because the compiler does not classify these specific SVG attributes correctly, it allows attackers to bypass Angular's built-in security protections.

When template binding is used to assign user-controlled data to these attributes for example, `<script [attr.href]="userInput">` the compiler treats the value as a standard string or a non-sensitive URL rather than a resource link. This enables an attacker to provide a malicious payload, such as a `data:text/javascript` URI or a link to an external malicious script.

### Impact
When successfully exploited, this vulnerability allows for **arbitrary JavaScript execution** within the context of the victim's browser session. This can lead to:
- **Session Hijacking:** Stealing session cookies, localStorage data, or authentication tokens.
- **Data Exfiltration:** Accessing and transmitting sensitive information displayed within the application.
- **Unauthorized Actions:** Performing state-changing actions (like clicking buttons or submitting forms) on behalf of the authenticated user.

### Attack Preconditions

1. The victim application must explicitly use SVG `<script>` elements within its templates.
2. The application must use property or attribute binding (interpolation) for the `href` or `xlink:href` attributes of those SVG scripts.
3. The data bound to these attributes must be derived from an untrusted source (e.g., URL parameters, user-submitted database entries, or unsanitized API responses).

### Patches
- 19.2.18
- 20.3.16
- 21.0.7
- 21.1.0-rc.0

### Workarounds
Until the patch is applied, developers should:

- **Avoid Dynamic Bindings**: Do not use Angular template binding (e.g., `[attr.href]`) for SVG `<script>` elements.
- **Input Validation**: If dynamic values must be used, strictly validate the input against a strict allowlist of trusted URLs on the server side or before it reaches the template.

### Resources

- https://github.com/angular/angular/pull/66318

## References
- https://github.com/angular/angular/security/advisories/GHSA-jrmj-c5cx-3cw6
- https://nvd.nist.gov/vuln/detail/CVE-2026-22610
- https://github.com/angular/angular/pull/66318
- https://github.com/angular/angular/commit/91dc91bae4a1bbefc58bef6ef739d0e02ab44d56
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://cert-portal.siemens.com/productcert/html/ssa-485750.html
- https://github.com/angular/angular
