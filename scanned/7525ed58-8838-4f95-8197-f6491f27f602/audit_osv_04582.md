# [M] Discourse: Templates endpoint exposes hidden tag names

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-72732
Aliases: CVE-2026-72732, GHSA-xrgc-52m8-82hm
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-discourse-2026-72732
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.6.0 <2026.6.1

## Details
Discourse is an open-source discussion platform. Prior to 2026.1.6, 2026.5.2, 2026.6.1, and 2026.7.0, the discourse_templates endpoint exposed hidden tag names because DiscourseTemplates::TemplatesSerializer in plugins/discourse-templates/app/serializers/discourse_templates/templates_serializer.rb did not filter tags through the request Guardian. The serializer did not respect tag group permissions, allowing users to see tags they were not permitted to view. This issue is fixed in versions 2026.1.6, 2026.5.2, 2026.6.1, and 2026.7.0.

## References
- https://github.com/discourse/discourse/commit/25e9d55b4c652b8dc1c90f44c40c8f3fec77748c
- https://github.com/discourse/discourse/commit/c9b431b3b75727f7132ec231142371d203a6124b
- https://github.com/discourse/discourse/commit/f216f258bd473e6299c6aef7b6130e7db90116c0
- https://github.com/discourse/discourse/commit/f41e71b645eb60cc263e7a1de22251028115abf1
- https://github.com/discourse/discourse/security/advisories/GHSA-xrgc-52m8-82hm
- https://nvd.nist.gov/vuln/detail/CVE-2026-72732
