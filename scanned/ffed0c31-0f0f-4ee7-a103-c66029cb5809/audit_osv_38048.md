# [C] APTRS: Privilege Escalation via Mass Assignment of is_superuser in User Edit Endpoint

## Summary
Severity: Critical
Advisory: CVE-2026-34406
Aliases: GHSA-gv25-wp4h-9c35
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34406
Type: osv

## Details
APTRS (Automated Penetration Testing Reporting System) is a Python and Django-based automated reporting tool designed for penetration testers and security organizations. Prior to version 2.0.1, the edit_user endpoint (POST /api/auth/edituser/<pk>) allows Any user who can reach that endpoint and submit crafted permission to escalate their own account (or any other account) to superuser by including "is_superuser": true in the request body. The root cause is that CustomUserSerializer explicitly includes is_superuser in its fields list but omits it from read_only_fields, making it a writable field. The edit_user view performs no additional validation to prevent non-superusers from modifying this field. Once is_superuser is set to true, gaining unrestricted access to all application functionality without requiring re-authentication. This issue has been patched in version 2.0.1.

## References
- https://github.com/APTRS/APTRS/releases/tag/2.0.1
- https://github.com/APTRS/APTRS/security/advisories/GHSA-gv25-wp4h-9c35
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34406.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-34406
- https://github.com/APTRS/APTRS/commit/d1f1b3a5d1953082af8e075712ca29742e900d56
