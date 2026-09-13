# [M] Strapi Upload Plugin MIME Validation Bypass via Content API

## Summary
Severity: Medium
Advisory: GHSA-pcw7-5633-82vv
CVE: CVE-2026-22707
CWE: CWE-434, CWE-693
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-pcw7-5633-82vv
Type: github-advisory

## Affected
- npm: `@strapi/upload` — affected >=0 <5.33.3

## Details
### Summary of CVE-2026-22707 Vulnerability Details

- CVE: CVE-2026-22707
- CVSS v3.1 Vector: `CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N` (5.3 — Medium)
- Affected Versions: `@strapi/upload` <=5.33.2
- How to Patch: Immediately update your Strapi to >=5.33.3

### Description of CVE-2026-22707

In Strapi versions prior to 5.33.3, the Upload plugin's Content API endpoints did not enforce the administrator-configured MIME type restrictions (`plugin.upload.security.allowedTypes` and `deniedTypes`). The same restrictions were correctly enforced on the Admin Panel upload path.

The upload plugin's `enforceUploadSecurity` security check was invoked in the admin upload controller but was missing from the Content API controller. The Content API handlers `uploadFiles` and `replaceFile` (and the `upload` wrapper that dispatches to them) called the underlying upload service directly, bypassing both the magic-byte MIME detection and the configured allow/deny lists.

An authenticated user with the Content API upload permission could therefore upload file types the administrator had explicitly disallowed, including HTML and SVG content. In deployments serving uploaded files from the same origin as the admin panel (default), an attacker could upload an HTML or SVG file that, when opened directly by an admin, executed JavaScript in the admin origin, enabling admin-session hijack and authenticated administrative actions against the admin API.

The patch introduces a shared `prepareUploadRequest` helper that wraps `enforceUploadSecurity` and is called from both the Content API and admin upload controllers, ensuring identical security policy enforcement on every upload entry point.

### IoC's for CVE-2026-22707

Indicators that an instance running an unpatched version may have been exploited:

- Files in `/uploads/` with extensions outside the configured allow-list, particularly `.html`, `.htm`, `.svg`, `.js`, `.mjs`, `.xml`, or `.xhtml`. Filesystem regex: `\.(html?|svg|m?js|x?html|xml)$`
- Successful 201 responses from `POST /api/upload` where the uploaded file's MIME or extension is outside the configured `allowedTypes`
- Server access logs showing non-administrator users uploading files with executable web content types. Content-Type regex: `text/html|application/javascript|image/svg\+xml`
- Admin browsing logs (X-Forwarded-For, User-Agent) opening files under `/uploads/*.html` or `/uploads/*.svg` shortly before unexpected administrative actions (user creation, role changes, permission modifications)

## References

- **CWE-693**: Protection Mechanism Failure
- **CWE-434**: Unrestricted Upload of File with Dangerous Type
- **OWASP**: Unrestricted File Upload
- [Strapi 5 Documentation - Media Library](https://docs.strapi.io/cms/features/media-library)
- [Strapi Security Policy](https://github.com/strapi/strapi/security/policy)

## Credits

Reported independently by:
- @kaminuma (initial report, 2026-01-09)
- @arkmarta (concurrent report, 2026-01-13 — originally filed as GHSA-r7hp-523c-r8wr, closed as duplicate)

## References
- https://github.com/strapi/strapi/security/advisories/GHSA-pcw7-5633-82vv
- https://nvd.nist.gov/vuln/detail/CVE-2026-22707
- https://github.com/strapi/strapi
