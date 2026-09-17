# [H] SimpleChat plugin validation endpoints missing authentication and authorization

## Summary
Severity: High
Advisory: CVE-2026-57206
Aliases: GHSA-g6gr-xp46-hrmj
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-57206
Type: osv

## Details
SimpleChat is a secure AI conversation application with personal and group workspaces for document-grounded interactions. Prior to 0.241.206, several plugin validation routes in application/single_app/plugin_validation_endpoint.py, including `POST /api/admin/plugins/test-instantiation`, `GET /api/admin/plugins/health-check/<plugin_name>`, `POST /api/admin/plugins/repair/<plugin_name>`, and `POST /api/plugins/validate`, relied on @swagger_route(security=get_auth_security()) documentation without enforcing @login_required, @user_required, or @admin_required at runtime, allowing unauthenticated or unauthorized clients to invoke plugin validation, health, and repair behavior. This issue is fixed in version 0.241.206.

## References
- https://github.com/microsoft/simplechat/blob/main/docs/explanation/fixes/PLUGIN_VALIDATION_ROUTE_AUTH_FIX.md
- https://github.com/microsoft/simplechat/releases/tag/v0.250.001
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57206.json
- https://github.com/microsoft/simplechat/security/advisories/GHSA-g6gr-xp46-hrmj
- https://nvd.nist.gov/vuln/detail/CVE-2026-57206
