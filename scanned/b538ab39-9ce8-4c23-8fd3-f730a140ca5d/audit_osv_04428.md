# [M] Denial of service through invites in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2024-27085
Aliases: CVE-2024-27085, GHSA-cvp5-h7p8-mjj6
Ecosystem: Bitnami
Published: 2024-04-01
Source: https://osv.dev/vulnerability/BIT-discourse-2024-27085
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.2.1

## Details
Discourse is an open source platform for community discussion. In affected versions users that are allowed to invite others can inject arbitrarily large data in parameters used in the invite route. The problem has been patched in the latest version of Discourse. Users are advised to upgrade. Users unable to upgrade should disable invites or restrict access to them using the `invite allowed groups` site setting.

## References
- https://github.com/discourse/discourse/commit/62ea382247c1f87361d186392c45ca74c83be295
- https://github.com/discourse/discourse/security/advisories/GHSA-cvp5-h7p8-mjj6
- https://nvd.nist.gov/vuln/detail/CVE-2024-27085
