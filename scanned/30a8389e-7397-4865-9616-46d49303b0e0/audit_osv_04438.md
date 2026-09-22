# [M] Denial of service via Watched Words in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2024-38360
Aliases: CVE-2024-38360, GHSA-68pm-hm8x-pq2p
Ecosystem: Bitnami
Published: 2024-07-17
Source: https://osv.dev/vulnerability/BIT-discourse-2024-38360
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.2.3

## Details
Discourse is an open source platform for community discussion. In affected versions by creating replacement words with an almost unlimited number of characters, a moderator can reduce the availability of a Discourse instance. This issue has been addressed in stable version 3.2.3 and in current betas. Users are advised to upgrade. Users unable to upgrade may manually remove the long watched words either via SQL or Rails console.

## References
- https://github.com/discourse/discourse/commit/7b53e610c17e38be982dffefa4e5b5a709a3b990
- https://github.com/discourse/discourse/security/advisories/GHSA-68pm-hm8x-pq2p
- https://nvd.nist.gov/vuln/detail/CVE-2024-38360
