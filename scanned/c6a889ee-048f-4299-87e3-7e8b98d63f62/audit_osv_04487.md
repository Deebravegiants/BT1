# [H] Discourse has IDOR vulnerability in the directory items endpoint

## Summary
Severity: High
Advisory: BIT-discourse-2026-26265
Aliases: CVE-2026-26265, GHSA-crxf-p6jm-vpgw
Ecosystem: Bitnami
Published: 2026-03-03
Source: https://osv.dev/vulnerability/BIT-discourse-2026-26265
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.1.0 <2026.1.1

## Details
Discourse is an open source discussion platform. Prior to versions 2025.12.2, 2026.1.1, and 2026.2.0, an IDOR vulnerability in the directory items endpoint allows any user, including anonymous users, to retrieve private user field values for all users in the directory. The `user_field_ids` parameter in `DirectoryItemsController#index` accepts arbitrary user field IDs without authorization checks, bypassing the visibility restrictions (`show_on_profile` / `show_on_user_card`) that are enforced elsewhere (e.g., `UserCardSerializer` via `Guardian#allowed_user_field_ids`). An attacker can request `GET /directory_items.json?period=all&user_field_ids=<id>` with any private field ID and receive that field's value for every user in the directory response. This enables bulk exfiltration of private user data such as phone numbers, addresses, or other sensitive custom fields that admins have explicitly configured as non-public. The issue is patched in versions 2025.12.2, 2026.1.1, and 2026.2.0 by filtering `user_field_ids` against `UserField.public_fields` for non-staff users before building the custom field map. As a workaround, site administrators can remove sensitive data from private user fields, or disable the user directory via the `enable_user_directory` site setting.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-crxf-p6jm-vpgw
- https://nvd.nist.gov/vuln/detail/CVE-2026-26265
