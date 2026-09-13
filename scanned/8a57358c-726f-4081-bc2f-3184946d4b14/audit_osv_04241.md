# [H] authentik: Privilege Escalation via User PATCH: Superuser Group Assignment Bypasses enable_group_superuser

## Summary
Severity: High
Advisory: BIT-authentik-2026-40172
Aliases: CVE-2026-40172, GHSA-h6x7-hjjc-wjc9
Ecosystem: Bitnami
Published: 2026-06-01
Source: https://osv.dev/vulnerability/BIT-authentik-2026-40172
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2026.2.0 <2026.2.3

## Details
authentik is an open-source identity provider. In versions prior to 2025.12.5 and 2026.2.0 through 2026.2.2, the PATCH /api/v3/core/users/{pk}/ API allows a caller with change_user on a target user to assign arbitrary groups through UserSerializer, including groups with is_superuser=True, without requiring enable_group_superuser, leading to privilege escalation. This bypasses the stricter permission model enforced in group-management paths and enables delegated user-management permissions to escalate target users to administrator-equivalent privilege. Users with permissions to update groups or permissions to update users are able to add themselves or other users they have permissions on to users which have superuser permissions. This issue has been fixed in versions 22025.12.5 and 2026.2.3.

## References
- https://github.com/goauthentik/authentik/releases/tag/version%2F2025.12.5
- https://github.com/goauthentik/authentik/releases/tag/version%2F2026.2.3
- https://github.com/goauthentik/authentik/security/advisories/GHSA-h6x7-hjjc-wjc9
- https://nvd.nist.gov/vuln/detail/CVE-2026-40172
