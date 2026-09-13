# [M] Lemmy: Lower-ranked federated moderator can remove higher-ranked moderators

## Summary
Severity: Medium
Advisory: CVE-2026-54740
Aliases: GHSA-xmpx-2j2f-c7g7
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-54740
Type: osv

## Details
Lemmy is a link aggregator and forum for the fediverse. Prior to 0.19.19 and 1.0.0-alpha.18, a lower-ranked remote moderator can remove a higher-ranked moderator by sending a signed ActivityPub Remove activity to the target instance. The local API uses LocalUser::is_higher_mod_or_admin_check to enforce moderator rank, but CollectionRemove::verify in crates/apub/activities/src/community/collection_remove.rs only calls verify_mod_action. CollectionRemove::receive dereferences self.object as an ApubPerson, creates a CommunityModeratorForm, and calls CommunityActions::leave without checking that the actor outranks the moderator identified by the object field. In communities with federated moderators, a junior moderator can therefore strip senior moderators from the community moderator list even though the local API rejects the same action. This issue is fixed in versions 0.19.19 and 1.0.0-alpha.18.

## References
- https://github.com/LemmyNet/lemmy/releases/tag/0.19.19
- https://github.com/LemmyNet/lemmy/releases/tag/1.0.0-alpha.18
- https://join-lemmy.org/news/2026-06-09_-_Lemmy_Release_v0.19.19
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54740.json
- https://github.com/LemmyNet/lemmy/security/advisories/GHSA-xmpx-2j2f-c7g7
- https://nvd.nist.gov/vuln/detail/CVE-2026-54740
- https://github.com/LemmyNet/lemmy/commit/d127e714a66f34f6b9c8ea15f20097ac907cdf28
- https://github.com/LemmyNet/lemmy/commit/ede1d348344ca2027fd1bc6a0cab25575c0c3a4c
- https://github.com/LemmyNet/lemmy/pull/6475
- https://github.com/LemmyNet/lemmy/pull/6478
