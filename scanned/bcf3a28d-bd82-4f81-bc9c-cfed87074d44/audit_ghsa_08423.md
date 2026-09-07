# [M] NocoDB: Reflected Cross-Site Scripting via Page Leaving Redirect URL

## Summary
Severity: Medium
Advisory: GHSA-9qgr-6vpg-9gh9
CVE: CVE-2026-46547
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-9qgr-6vpg-9gh9
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0

## Details
### Summary
A reflected XSS vulnerability exists in the Page Leaving Warning page. The `ncRedirectUrl` and `ncBackUrl` query parameters are used in `window.location.href` and `<a>` tag bindings without validation, allowing `javascript:` URI injection.

### Details
`PageLeavingWarning.vue` reads `ncRedirectUrl` and `ncBackUrl` directly from the route query without validation. When `isSameOriginUrl()` returns `false` (as it does for `javascript:` URIs), the raw URL is assigned to `window.location.href`, executing arbitrary JavaScript. The redirect URL is also bound directly to an `<a>` tag's `href` attribute.

### Impact
An attacker can execute arbitrary JavaScript in the context of the NocoDB application by sending a crafted link to a victim. No authentication is required.

### Credit
This issue was reported by [@naoyashiga](https://github.com/naoyashiga).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-9qgr-6vpg-9gh9
- https://nvd.nist.gov/vuln/detail/CVE-2026-46547
- https://github.com/nocodb/nocodb
