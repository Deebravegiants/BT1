# [M] Payload: Server-Side Request Forgery (SSRF) in External File URL Uploads

## Summary
Severity: Medium
Advisory: GHSA-hhfx-5x8j-f5f6
CVE: CVE-2026-27567
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-hhfx-5x8j-f5f6
Type: github-advisory

## Affected
- npm: `payload` — affected >=0 <3.75.0

## Details
### Impact

A Server-Side Request Forgery (SSRF) vulnerability exists in Payload's external file upload functionality. When processing external URLs for file uploads, insufficient validation of HTTP redirects could allow an authenticated attacker to access internal network resources.

**Users are affected if ALL of these are true**:

- Payload version < v3.75.0
- At least one collection with `upload` enabled
- A user has `create` access to that upload-enabled collection

An authenticated user with upload collection write permissions could potentially access internal services. Response content from internal services could be retrieved through the application.

### Patches

This vulnerability has been patched in v3.75.0. Users should upgrade to v3.75.0 or later.

### Workarounds

If users cannot upgrade immediately, they can mitigate this vulnerability by disabling external file uploads via the `disableExternalFile` upload collection option, or by restricting `create` access on upload-enabled collections to **trusted users only**.

## References
- https://github.com/payloadcms/payload/security/advisories/GHSA-hhfx-5x8j-f5f6
- https://nvd.nist.gov/vuln/detail/CVE-2026-27567
- https://github.com/payloadcms/payload/commit/1041bb6
- https://github.com/payloadcms/payload
- https://github.com/payloadcms/payload/releases/tag/v3.75.0
