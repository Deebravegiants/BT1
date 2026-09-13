# [M] Disclosure of the existence of secret subcategories in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2024-24748
Aliases: CVE-2024-24748, GHSA-3qh8-xw23-cq4x
Ecosystem: Bitnami
Published: 2024-04-01
Source: https://osv.dev/vulnerability/BIT-discourse-2024-24748
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.2.1

## Details
Discourse is an open source platform for community discussion. In affected versions an attacker can learn that a secret subcategory exists under a public category which has no public subcategories. The issue is patched in the latest stable, beta and tests-passed version of Discourse. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/discourse/discourse/commit/819361ba28f86a1347059af300bb5cca690f9193
- https://github.com/discourse/discourse/security/advisories/GHSA-3qh8-xw23-cq4x
- https://nvd.nist.gov/vuln/detail/CVE-2024-24748
