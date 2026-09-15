# [M] Discourse doesn't scope reviewable notes to user-visible reviewables

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-26973
Aliases: CVE-2026-26973, GHSA-c587-qx78-vhmx
Ecosystem: Bitnami
Published: 2026-03-03
Source: https://osv.dev/vulnerability/BIT-discourse-2026-26973
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.1.0 <2026.1.1

## Details
Discourse is an open source discussion platform. Versions prior to 2025.12.2, 2026.1.1, and 2026.2.0 have an IDOR (Insecure Direct Object Reference) in `ReviewableNotesController`. When `enable_category_group_moderation` is enabled, a user belonging to a  category moderation group can create or delete their own notes on **any** reviewable in the system, including reviewables in categories they do not moderate. The controller used an unscoped `Reviewable.find` and the `ensure_can_see` guard only checked whether the user could access the review queue in general, not whether they could access the specific reviewable. Only instances with `enable_category_group_moderation` enabled are affected. Staff users (admins/moderators) are not impacted as they already have access to all reviewables. The issue is patched in versions 2025.12.2, 2026.1.1, and 2026.2.0 by scoping the reviewable lookup through `Reviewable.viewable_by(current_user)`. As a workaround, disable the `enable_category_group_moderation` site setting. This removes the attack surface as only staff users will have access to the review queue.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-c587-qx78-vhmx
- https://nvd.nist.gov/vuln/detail/CVE-2026-26973
