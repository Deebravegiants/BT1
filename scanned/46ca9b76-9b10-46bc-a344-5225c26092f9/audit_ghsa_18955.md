# [H] Angular is Vulnerable to XSRF Token Leakage via Protocol-Relative URLs in Angular HTTP Client

## Summary
Severity: High
Advisory: GHSA-58c5-g7wp-6w37
CVE: CVE-2025-66035
CWE: CWE-201, CWE-359
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2025-11-26
Source: https://github.com/advisories/GHSA-58c5-g7wp-6w37
Type: github-advisory

## Affected
- npm: `@angular/common` — affected >=21.0.0-next.0 <21.0.1
- npm: `@angular/common` — affected >=20.0.0-next.0 <20.3.14
- npm: `@angular/common` — affected >=0 <19.2.16

## Details
The vulnerability is a **Credential Leak by App Logic** that leads to the **unauthorized disclosure of the Cross-Site Request Forgery (XSRF) token** to an attacker-controlled domain.

Angular's HttpClient has a built-in XSRF protection mechanism that works by checking if a request URL starts with a protocol (`http://` or `https://`) to determine if it is cross-origin. If the URL starts with protocol-relative URL (`//`), it is incorrectly treated as a same-origin request, and the XSRF token is automatically added to the `X-XSRF-TOKEN` header.

### Impact
The token leakage completely bypasses Angular's built-in CSRF protection, allowing an attacker to capture the user's valid XSRF token. Once the token is obtained, the attacker can perform arbitrary Cross-Site Request Forgery (CSRF) attacks against the victim user's session.

### Attack Preconditions
1. The victim's Angular application must have **XSRF protection enabled**.  
2. The attacker must be able to make the application send a state-changing HTTP request (e.g., `POST`) to a **protocol-relative URL**  (e.g., `//attacker.com`) that they control.

### Patches
- 19.2.16
- 20.3.14
- 21.0.1

### Workarounds
Developers should avoid using protocol-relative URLs (URLs starting with `//`) in HttpClient requests. All backend communication URLs should be hardcoded as relative paths (starting with a single `/`) or fully qualified, trusted absolute URLs.

## References
- https://github.com/angular/angular/security/advisories/GHSA-58c5-g7wp-6w37
- https://nvd.nist.gov/vuln/detail/CVE-2025-66035
- https://github.com/angular/angular/commit/0276479e7d0e280e0f8d26fa567d3b7aa97a516f
- https://github.com/angular/angular/commit/05fe6686a97fa0bcd3cf157805b3612033f975bc
- https://github.com/angular/angular/commit/3240d856d942727372a705252f7c8c115394a41e
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://cert-portal.siemens.com/productcert/html/ssa-485750.html
- https://github.com/angular/angular
- https://github.com/angular/angular/releases/tag/19.2.16
- https://github.com/angular/angular/releases/tag/20.3.14
- https://github.com/angular/angular/releases/tag/21.0.1
