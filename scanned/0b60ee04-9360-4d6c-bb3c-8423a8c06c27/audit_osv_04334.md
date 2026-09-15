# [M] Post creator of a whisper post can be revealed to non-staff users in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2021-32788
Aliases: CVE-2021-32788, GHSA-v6xg-q577-vc92
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2021-32788
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.7.7

## Details
Discourse is an open source discussion platform. In versions prior to 2.7.7 there are two bugs which led to the post creator of a whisper post being revealed to non-staff users. 1: Staff users that creates a whisper post in a personal message is revealed to non-staff participants of the personal message even though the whisper post cannot be seen by them. 2: When a whisper post is before the last post in a post stream, deleting the last post will result in the creator of the whisper post to be revealed to non-staff users as the last poster of the topic.

## References
- https://github.com/discourse/discourse/commit/680024f9071b7696e5a444a58791016c6dc1f1e5
- https://github.com/discourse/discourse/commit/dbdf61196d9e964e8823793d2e7f856595fea4d9
- https://github.com/discourse/discourse/security/advisories/GHSA-v6xg-q577-vc92
- https://nvd.nist.gov/vuln/detail/CVE-2021-32788
