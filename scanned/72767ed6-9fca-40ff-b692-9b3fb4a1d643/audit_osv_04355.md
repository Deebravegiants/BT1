# [M] Private group name exposure in discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2022-24804
Aliases: CVE-2022-24804, GHSA-v4c9-6m9g-37ff
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-24804
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.8.3

## Details
Discourse is an open source platform for community discussion. In stable versions prior to 2.8.3 and beta versions prior 2.9.0.beta4 erroneously expose groups. When a group with restricted visibility has been used to set the permissions of a category, the name of the group is leaked to any user that is able to see the category. To workaround the problem, a site administrator can remove groups with restricted visibility from any category's permissions setting.

## References
- https://github.com/discourse/discourse/commit/0f7b9878ff3207ce20970f0517604793920bb3d2
- https://github.com/discourse/discourse/security/advisories/GHSA-v4c9-6m9g-37ff
- https://nvd.nist.gov/vuln/detail/CVE-2022-24804
