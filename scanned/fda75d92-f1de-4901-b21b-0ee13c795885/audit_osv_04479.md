# [H] Discourse moderators can access admin-only reports exposing private upload URLs

## Summary
Severity: High
Advisory: BIT-discourse-2025-69218
Aliases: CVE-2025-69218, GHSA-79f9-j8h4-3w6w
Ecosystem: Bitnami
Published: 2026-02-02
Source: https://osv.dev/vulnerability/BIT-discourse-2025-69218
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.1.0 <2026.1.0

## Details
Discourse is an open source discussion platform. In versions prior to 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0, moderators can access the `top_uploads` admin report which should be restricted to admins only. This report displays direct URLs to all uploaded files on the site, including sensitive content such as user data exports, admin backups, and other private attachments that moderators should not have access to. This issue is patched in versions 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0. There is no workaround. Limit moderator privileges to trusted users until the patch is applied.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-79f9-j8h4-3w6w
- https://nvd.nist.gov/vuln/detail/CVE-2025-69218
