# [M] Angular: Template and Attribute Namespace Sanitization Bypass (XSS)

## Summary
Severity: Medium
Advisory: GHSA-f3m7-gqxr-g87x
CVE: CVE-2026-50557
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-f3m7-gqxr-g87x
Type: github-advisory

## Affected
- npm: `@angular/core` — affected >=21.0.0-next.0 <21.2.15
- npm: `@angular/core` — affected >=22.0.0-next.0 <22.0.0-rc.2
- npm: `@angular/core` — affected >=20.0.0-next.0 <20.3.22
- npm: `@angular/core` — affected >=19.0.0-next.0 <19.2.22
- npm: `@angular/core` — affected >=0
- npm: `@angular/compiler` — affected >=21.0.0-next.0 <21.2.15
- npm: `@angular/compiler` — affected >=22.0.0-next.0 <22.0.0-rc.2
- npm: `@angular/compiler` — affected >=20.0.0-next.0 <20.3.22
- npm: `@angular/compiler` — affected >=19.0.0-next.0 <19.2.22
- npm: `@angular/compiler` — affected >=0

## Details
An issue in the `@angular/compiler` and `@angular/core` packages allows bypassing element and attribute sanitization/validation through specific namespace workarounds.

Specifically, namespaced script elements (e.g., `<svg:script>` or `<:svg:script>`) were not properly identified as script elements by the Angular template preparser, allowing them to pass through template compilation without being stripped.

Furthermore, security context schema mappings for element attributes did not consistently handle attributes within namespaced elements (like SVG and MathML), opening up gaps where malicious namespaced attributes could bypass runtime and compile-time sanitizers.

Combined, these flaws enable an attacker who can inject or supply a template/tag structure with custom namespaces to bypass Angular's script-stripping logic and attribute sanitizers, leading to client-side Cross-Site Scripting (XSS).

### Impact
Any Angular application that compiles user-controlled templates at runtime, or relies on sanitization of namespaced elements/attributes, is vulnerable to this security bypass.

Once exploited, this allows a malicious actor to inject a namespaced script element or dynamic attribute bindings, bypassing core sanitization constraints to execute arbitrary JavaScript within the target user's browser context. This could lead to session hijacking, sensitive data exposure, or unauthorized actions on behalf of the user.

### Attack Preconditions
To successfully exploit these vulnerabilities, the following environment parameters and application states must all concurrently exist:
1. **User-Controlled Template Input:** The application must accept user-controlled inputs that are directly processed by the Angular template compiler at runtime.
2. **Namespace Parsing Support:** The input structure must employ custom namespace prefixes (such as `<svg:script>`) to evade standard tag-name blocklists/checks.
3. **Absence of Additional Context Sanitization:** The application does not perform separate input sanitization before feeding values to the Angular compiler.

### Patches
* 22.0.0-rc.2
* 21.2.15
* 20.3.22
* 19.2.23

## References
- https://github.com/angular/angular/security/advisories/GHSA-f3m7-gqxr-g87x
- https://nvd.nist.gov/vuln/detail/CVE-2026-50557
- https://github.com/angular/angular/pull/68689
- https://github.com/angular/angular/pull/68868
- https://github.com/angular/angular
