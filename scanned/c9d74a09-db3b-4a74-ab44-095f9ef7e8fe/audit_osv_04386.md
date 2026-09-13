# [M] Regular expression denial of service via installing themes via git in discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-25167
Aliases: CVE-2023-25167, GHSA-4w55-w26q-r35w
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-25167
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.0.1

## Details
Discourse is an open source discussion platform. In affected versions a malicious user can cause a regular expression denial of service using a carefully crafted git URL. This issue is patched in the latest stable, beta and tests-passed versions of Discourse. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/discourse/discourse/commit/ec4c30270887366dc28788bc4ab8a22a098573cd
- https://github.com/discourse/discourse/security/advisories/GHSA-4w55-w26q-r35w
- https://nvd.nist.gov/vuln/detail/CVE-2023-25167
