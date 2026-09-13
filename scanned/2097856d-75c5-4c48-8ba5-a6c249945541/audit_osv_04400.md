# [M] Topic Title Validation Skipped When Changing Category in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-36466
Aliases: CVE-2023-36466, GHSA-4hjh-wg43-p932
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-36466
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.0.5

## Details
Discourse is an open source discussion platform. When editing a topic, there is a vulnerability that enables a user to bypass the topic title validations for things like title length, number of emojis in title and blank topic titles. The issue is patched in the latest stable, beta and tests-passed version of Discourse.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-4hjh-wg43-p932
- https://nvd.nist.gov/vuln/detail/CVE-2023-36466
