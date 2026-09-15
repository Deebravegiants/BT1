# [M] Discourse Allows Unauthorized Access to Deleted Posts Index via Group Membership

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-33428
Aliases: CVE-2026-33428, GHSA-frcw-p4mc-x6mp
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-33428
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Prior to versions 2026.3.0, 2026.2.1, and 2026.1.2, a non-staff user with elevated group membership could access deleted posts belonging to any user due to an overly broad authorization check on the deleted posts index endpoint. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-frcw-p4mc-x6mp
- https://nvd.nist.gov/vuln/detail/CVE-2026-33428
