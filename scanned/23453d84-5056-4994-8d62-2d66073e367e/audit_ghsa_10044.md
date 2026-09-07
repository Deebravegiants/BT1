# [M] @adonisjs/http-server has an Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6qvv-pj99-48qm
CVE: CVE-2026-40255
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-6qvv-pj99-48qm
Type: github-advisory

## Affected
- npm: `@adonisjs/http-server` — affected >=8.0.0-next.0 <8.2.0
- npm: `@adonisjs/core` — affected >=0 <7.3.1
- npm: `@adonisjs/http-server` — affected >=0 <7.8.1

## Details
### Impact

The `response.redirect().back()` method in `@adonisjs/http-server` is vulnerable to open redirects. The method reads the `Referer` header from the incoming HTTP request and redirects to that URL without validating the host. An attacker who can influence the `Referer` header (for example, by linking a user through an attacker-controlled page before a form submission) can cause the application to redirect users to a malicious external site.

This affects all AdonisJS applications that use `response.redirect().back()` or `response.redirect('back')`.

The vulnerability is classified as CWE-601: URL Redirection to Untrusted Site ('Open Redirect').

### Patches

This has been fixed in `@adonisjs/http-server` version **8.2.0**. The `back()` method now validates the `Referer` header's host against the request's own `Host` header. Referrers from unrecognized hosts are rejected and the redirect falls back to `/` (or a developer-provided fallback URL).

Applications that operate across multiple domains can configure additional trusted hosts via the `redirect.allowedHosts` option in `config/app.ts`.

Users should upgrade to `@adonisjs/http-server@^8.2.0` (or `@adonisjs/core@^7.4.0` if using the core meta-package).

### Workarounds

If upgrading is not immediately possible, avoid using `response.redirect().back()` in routes that are reachable by unauthenticated users or from pages that accept external traffic. Instead, redirect to a known safe path explicitly using `response.redirect().toPath('/dashboard')`.

### References

- [CWE-601: URL Redirection to Untrusted Site](https://cwe.mitre.org/data/definitions/601.html)
- [OWASP: Unvalidated Redirects and Forwards](https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html)

## References
- https://github.com/adonisjs/http-server/security/advisories/GHSA-6qvv-pj99-48qm
- https://nvd.nist.gov/vuln/detail/CVE-2026-40255
- https://github.com/adonisjs/http-server/commit/2008fb6cf4f6f1c0ca5797d57def4d93e1c3de08
- https://github.com/adonisjs/http-server
- https://github.com/adonisjs/http-server/releases/tag/v7.8.1
- https://github.com/adonisjs/http-server/releases/tag/v8.2.0
