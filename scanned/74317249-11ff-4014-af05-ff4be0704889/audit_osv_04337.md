# [M] Information exposure in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2021-37703
Aliases: CVE-2021-37703, GHSA-gq2h-qhg2-phf9
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2021-37703
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.7.8

## Details
Discourse is an open-source platform for community discussion. In Discourse before versions 2.7.8 and 2.8.0.beta5, a user's read state for a topic such as the last read post number and the notification level is exposed.

## References
- https://github.com/discourse/discourse/commit/aed65ec16d38886d7be7209d8c02df4ffd4937a4
- https://github.com/discourse/discourse/security/advisories/GHSA-gq2h-qhg2-phf9
- https://nvd.nist.gov/vuln/detail/CVE-2021-37703
