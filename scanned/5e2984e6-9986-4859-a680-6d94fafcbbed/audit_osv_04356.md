# [M] Category group permissions leaked in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2022-24850
Aliases: CVE-2022-24850, GHSA-34xr-ff4w-mcpf
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-24850
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.8.2

## Details
Discourse is an open source platform for community discussion. A category's group permissions settings can be viewed by anyone that has access to the category. As a result, a normal user is able to see whether a group has read/write permissions in the category even though the information should only be available to the users that can manage a category. This issue is patched in the latest stable, beta and tests-passed versions of Discourse. There are no workarounds for this problem.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-34xr-ff4w-mcpf
- https://nvd.nist.gov/vuln/detail/CVE-2022-24850
