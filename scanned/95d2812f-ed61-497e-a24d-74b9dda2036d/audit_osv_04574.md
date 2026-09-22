# [M] Discourse: Anonymous sidebar serialization exposes descriptions of category-restricted tags

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-72723
Aliases: CVE-2026-72723, GHSA-4p6q-h74v-5j7p
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-discourse-2026-72723
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.6.0 <2026.6.1

## Details
Discourse is an open-source discussion platform. Prior to 2026.1.6, 2026.5.2, 2026.6.1, and 2026.7.0, SiteSerializer.anonymous_default_navigation_menu_tags serializes tags from SiteSetting.default_navigation_menu_tags without applying DiscourseTagging.filter_visible for the anonymous viewer. An unauthenticated user can retrieve restricted tag names and descriptions through /site.json when those tags are limited by inaccessible categories, category tag groups, or tag-group permissions. This issue is fixed in versions 2026.1.6, 2026.5.2, 2026.6.1, and 2026.7.0.

## References
- https://github.com/discourse/discourse/commit/0248e9ca82d0493037a9ca04d73904ccfad795f9
- https://github.com/discourse/discourse/commit/03444ddb74d535dda557350f4c5800a6ec2669d7
- https://github.com/discourse/discourse/commit/900f51c147913f667e64484c2f2dd48c723314ac
- https://github.com/discourse/discourse/commit/da84c677213cac3b024e753f180f45472b89efde
- https://github.com/discourse/discourse/pull/42091
- https://github.com/discourse/discourse/pull/42092
- https://github.com/discourse/discourse/pull/42093
- https://github.com/discourse/discourse/pull/42094
- https://github.com/discourse/discourse/security/advisories/GHSA-4p6q-h74v-5j7p
- https://nvd.nist.gov/vuln/detail/CVE-2026-72723
