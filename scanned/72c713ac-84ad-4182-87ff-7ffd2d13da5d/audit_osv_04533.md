# [M] Discourse hardens chat DM channel creation and expansion

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-33410
Aliases: CVE-2026-33410, GHSA-2m5j-6v2r-cq2h
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-33410
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Versions prior to 2026.3.0, 2026.2.1, and 2026.1.2 have two authorization issues in the chat direct message API. First, when creating a direct message channel or adding users to an existing one, the `target_groups` parameter was passed directly to the user resolution query without checking group or member visibility for the acting user. An authenticated chat user could craft an API request with a known private/hidden group name and receive a channel containing that group's members, leaking their identities. Second, `can_chat?` only checked group membership, not the `chat_enabled` user preference. A chat-disabled user could create or query DM channels between other users via the direct messages API, potentially exposing private `last_message` content from the serialized channel response. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-2m5j-6v2r-cq2h
- https://nvd.nist.gov/vuln/detail/CVE-2026-33410
