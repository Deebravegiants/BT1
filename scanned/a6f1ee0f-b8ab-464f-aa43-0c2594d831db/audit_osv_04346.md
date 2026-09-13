# [M] Exposure of whisper participants in discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2022-21642
Aliases: CVE-2022-21642, GHSA-mx3h-vc7w-r9c6
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-21642
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.7.13

## Details
Discourse is an open source platform for community discussion. In affected versions when composing a message from topic the composer user suggestions reveals whisper participants. The issue has been patched in stable version 2.7.13 and beta version 2.8.0.beta11. There is no workaround for this issue and users are advised to upgrade.

## References
- https://github.com/discourse/discourse/commit/702685b6a06ae45a544fc702027f1e4573d94aaa
- https://github.com/discourse/discourse/security/advisories/GHSA-mx3h-vc7w-r9c6
- https://nvd.nist.gov/vuln/detail/CVE-2022-21642
