# [M] Arbitrary keys can be added to a topic's custom fields by any user in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-45147
Aliases: CVE-2023-45147, GHSA-wm89-m359-f9qv
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-45147
Type: osv

## Affected
- Bitnami: `discourse` — affected unspecified

## Details
Discourse is an open source community platform. In affected versions any user can create a topic and add arbitrary custom fields to a topic. The severity of this vulnerability depends on what plugins are installed and how the plugins uses topic custom fields. For a default Discourse installation with the default plugins, this vulnerability has no impact. The problem has been patched in the latest version of Discourse. Users are advised to update to version 3.1.1 if they are on the stable branch or 3.2.0.beta2 if they are on the beta branch. Users unable to upgrade should disable any plugins that access topic custom fields.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-wm89-m359-f9qv
- https://nvd.nist.gov/vuln/detail/CVE-2023-45147
