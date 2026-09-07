# [M] @angular/core: Angular Template and Dynamic Component Namespace Bypass leading to Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-692r-grfm-v8x7
CVE: CVE-2026-52725
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-692r-grfm-v8x7
Type: github-advisory

## Affected
- npm: `@angular/core` — affected >=21.0.0-next.0 <21.2.15
- npm: `@angular/core` — affected >=22.0.0-next.0 <22.0.0-rc.2
- npm: `@angular/core` — affected >=19.0.0-next.0 <19.2.23
- npm: `@angular/core` — affected >=0
- npm: `@angular/core` — affected >=20.0.0-next.0 <20.3.22

## Details
An issue in the `@angular/core` package allows bypassing script-execution restrictions during dynamic component creation.

Specifically, the dynamic component instantiation mechanism (`createComponent`) failed to reject mounting components directly onto a `<script>` or namespaced script element (such as `<svg:script>`). This enabled the initialization of custom components on a tag that executes scripts, allowing attackers to hijack or inject script-executing hosts.

This flaw enables an attacker who can control the host element or selector parameter passed to `createComponent` to initialize or mount an Angular component directly onto a `<script>` tag, leading to execution of untrusted code or client-side Cross-Site Scripting (XSS).

### Impact
Any Angular application that registers dynamic components based on user-supplied parameters (like selectors or host elements) is vulnerable to this security bypass.

Once exploited, this allows a malicious actor to mount a dynamic component on a script tag, bypassing core dynamic component creation safeguards to execute arbitrary JavaScript within the target user's browser context. This could lead to session hijacking, sensitive data exposure, or unauthorized actions on behalf of the user.

### Attack Preconditions
To successfully exploit these vulnerabilities, the following environment parameters and application states must all concurrently exist:
1. **User-Controlled Host Selection:** The application must accept user-controlled inputs that are passed as a selector/host element to `createComponent`.
2. **Absence of Additional Context Sanitization:** The application does not perform separate input sanitization before feeding values to the dynamic creation APIs.

### Patches
* 22.0.0-rc.2
* 21.2.15
* 20.3.22
* 19.2.23

## References
- https://github.com/angular/angular/security/advisories/GHSA-692r-grfm-v8x7
- https://nvd.nist.gov/vuln/detail/CVE-2026-52725
- https://github.com/angular/angular/pull/68686
- https://github.com/angular/angular/pull/68713
- https://github.com/angular/angular
