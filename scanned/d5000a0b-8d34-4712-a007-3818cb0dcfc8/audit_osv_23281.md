# [H] CVE-2022-46792

## Summary
Severity: High
Advisory: CVE-2022-46792
Aliases: GHSA-g7mj-g7f4-hgrg
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-08
Source: https://osv.dev/vulnerability/CVE-2022-46792
Type: osv

## Details
Hasura GraphQL Engine before 2.15.2 mishandles row-level authorization in the Update Many API for Postgres backends. The fixed versions are 2.10.2, 2.11.3, 2.12.1, 2.13.2, 2.14.1, and 2.15.2. (Versions before 2.10.0 are unaffected.)

## References
- https://groups.google.com/g/hasura-security-announce/c/kzK-uPAKGUU
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/46xxx/CVE-2022-46792.json
- https://github.com/hasura/graphql-engine/security/advisories/GHSA-g7mj-g7f4-hgrg
- https://nvd.nist.gov/vuln/detail/CVE-2022-46792
- https://hasura.io/blog/critical-vulnerability-in-hasuras-graphql-engine-v2-10-0/
