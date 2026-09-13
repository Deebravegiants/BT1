# [M] Presence of restricted personal Discourse messages may be leaked if tagged with a tag

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-23935
Aliases: CVE-2023-23935, GHSA-rf8j-mf8c-82v7
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-23935
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.0.1

## Details
Discourse is an open-source messaging platform. In versions 3.0.1 and prior on the `stable` branch and versions 3.1.0.beta2 and prior on the `beta` and `tests-passed` branches, the count of personal messages displayed for a tag is a count of all personal messages regardless of whether the personal message is visible to a given user. As a result, any users can technically poll a sensitive tag to determine if a new personal message is created even if the user does not have access to the personal message.

In the patched versions, the count of personal messages tagged with a given tag is hidden by default. To revert to the old behaviour of displaying the count of personal messages for a given tag, an admin may enable the `display_personal_messages_tag_counts` site setting.

## References
- https://github.com/discourse/discourse/commit/f31f0b70f82c43d93220ce6fc0d4f57440452f37
- https://github.com/discourse/discourse/security/advisories/GHSA-rf8j-mf8c-82v7
- https://nvd.nist.gov/vuln/detail/CVE-2023-23935
