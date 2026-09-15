# [M] Users can see other user's tagged PMs in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2024-56197
Aliases: CVE-2024-56197, GHSA-xmgr-g9cp-v239
Ecosystem: Bitnami
Published: 2025-02-20
Source: https://osv.dev/vulnerability/BIT-discourse-2024-56197
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.4.0

## Details
Discourse is an open source platform for community discussion. PM titles and metadata can be read by other users when the "PM tags allowed for groups" option is enabled, the other user is a member of a group added to this option, and the PM has been tagged. This issue has been patched in the latest `stable`, `beta` and `tests-passed` versions of Discourse. Users are advised to upgrade. Users unable to upgrade should remove all groups from the the "PM tags allowed for groups" option.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-xmgr-g9cp-v239
- https://nvd.nist.gov/vuln/detail/CVE-2024-56197
