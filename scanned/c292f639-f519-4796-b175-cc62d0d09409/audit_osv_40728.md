# [M] Hasura: Row-level authorization bypass on table computed fields

## Summary
Severity: Medium
Advisory: CVE-2026-54698
Aliases: GHSA-r27x-gc74-qmxh
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-54698
Type: osv

## Details
Hasura is an open-source product that provides users GraphQL or REST APIs. Prior to 2.49.2 and 2.45.5, a user can use a where clause on a table computed field (returning SETOF some_table) to infer row values that ought to be filtered for their role based on some_table's row-level permissions. While such rows cannot be returned directly, like predicates on strings for instance allow values to be brute forced efficiently with the where clause as an oracle. This issue is fixed in versions 2.49.2 and 2.45.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54698.json
- https://github.com/hasura/graphql-engine/security/advisories/GHSA-r27x-gc74-qmxh
- https://nvd.nist.gov/vuln/detail/CVE-2026-54698
