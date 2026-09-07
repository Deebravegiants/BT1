# [M] Payload has a CSRF Protection Bypass in Authentication Flow

## Summary
Severity: Medium
Advisory: GHSA-p6mr-xf3r-ghq4
CVE: CVE-2026-34749
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-p6mr-xf3r-ghq4
Type: github-advisory

## Affected
- npm: `payload` — affected >=0 <3.79.1

## Details
### Impact

A Cross-Site Request Forgery (CSRF) vulnerability existed in the authentication flow. Under certain conditions, the configured CSRF protection could be bypassed, allowing cross-site requests to be made.

Consumers are affected if ALL of these are true:

- Payload version **< v3.79.1**
- `serverURL` is configured

### Patches

This vulnerability has been patched in **v3.79.1**. Additional validation has been added to the authentication flow.

Consumers should upgrade to **v3.79.1** or later.

### Workarounds

There is no complete workaround without upgrading. 

If consumers cannot upgrade immediately, setting `cookies.sameSite` to `'Strict'` will prevent the session cookie from being sent cross-site. However, this will also require users to re-authenticate when navigating to the application from external links (e.g. email, other sites).

## References
- https://github.com/payloadcms/payload/security/advisories/GHSA-p6mr-xf3r-ghq4
- https://nvd.nist.gov/vuln/detail/CVE-2026-34749
- https://github.com/payloadcms/payload
- https://github.com/payloadcms/payload/releases/tag/v3.79.1
