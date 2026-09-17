# [M] Notifications leak in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2021-43792
Aliases: CVE-2021-43792, GHSA-pq2x-vq37-8522
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2021-43792
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.7.11

## Details
Discourse is an open source discussion platform. In affected versions a vulnerability affects users of tag groups who use the "Tags are visible only to the following groups" feature. A tag group may only allow a certain group (e.g. staff) to view certain tags. Users who were tracking or watching the tags via /preferences/tags, then have their staff status revoked will still see notifications related to the tag, but will not see the tag on each topic. This issue has been patched in stable version 2.7.11. Users are advised to upgrade as soon as possible.

## References
- https://github.com/discourse/discourse/commit/cdaf7f4bb3ec268238e4c29a14bb73fad56574b4
- https://github.com/discourse/discourse/security/advisories/GHSA-pq2x-vq37-8522
- https://meta.discourse.org/t/non-forum-staff-getting-notifications-for-staff-only-tags/184895
- https://nvd.nist.gov/vuln/detail/CVE-2021-43792
