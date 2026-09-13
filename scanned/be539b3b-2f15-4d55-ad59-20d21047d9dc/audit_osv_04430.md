# [H] Disclosure of the existence of secret categories with custom backgrounds in Discourse

## Summary
Severity: High
Advisory: BIT-discourse-2024-28242
Aliases: CVE-2024-28242, GHSA-c7q7-7f6q-2c23
Ecosystem: Bitnami
Published: 2024-04-01
Source: https://osv.dev/vulnerability/BIT-discourse-2024-28242
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.2.1

## Details
Discourse is an open source platform for community discussion. In affected versions an attacker can learn that secret categories exist when they have backgrounds set. The issue is patched in the latest stable, beta and tests-passed version of Discourse. Users are advised to upgrade. Users unable to upgrade should temporarily remove category backgrounds.

## References
- https://github.com/discourse/discourse/commit/b425fbc2a28341a5627928f963519006712c3d39
- https://github.com/discourse/discourse/security/advisories/GHSA-c7q7-7f6q-2c23
- https://nvd.nist.gov/vuln/detail/CVE-2024-28242
