# [M] Discourse: Presence of read restricted topics may be leaked if tagged with a tag that is visible to all users

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-23622
Aliases: CVE-2023-23622, GHSA-2wvr-4x7w-v795
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-23622
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.0.0

## Details
Discourse is an open-source discussion platform. Prior to version 3.0.1 of the `stable` branch and version 3.1.0.beta2 of the `beta` and `tests-passed` branches, the count of topics displayed for a tag is a count of all regular topics regardless of whether the topic is in a read restricted category or not. As a result, any users can technically poll a sensitive tag to determine if a new topic is created in a category which the user does not have excess to. 

In version 3.0.1 of the `stable` branch and version 3.1.0.beta2 of the `beta` and `tests-passed` branches, the count of topics displayed for a tag defaults to only counting regular topics which are not in read restricted categories. Staff users will continue to see a count of all topics regardless of the topic's category read restrictions.

## References
- https://github.com/discourse/discourse/commit/105fee978d73b0ec23ff814a09d1c0c9ace95164
- https://github.com/discourse/discourse/commit/ecb9aa5dba94741d9579f4f873f0675f48b4184f
- https://github.com/discourse/discourse/pull/20004
- https://github.com/discourse/discourse/pull/20005
- https://github.com/discourse/discourse/security/advisories/GHSA-2wvr-4x7w-v795
- https://nvd.nist.gov/vuln/detail/CVE-2023-23622
