# [H] Unauthenticated path traversal vulnerability in Hasura GraphQL Engine

## Summary
Severity: High
Advisory: CVE-2023-27588
Aliases: GHSA-c9rw-rw2f-mj4x
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-03-14
Source: https://osv.dev/vulnerability/CVE-2023-27588
Type: osv

## Details
Hasura is an open-source product that provides users GraphQL or REST APIs. A path traversal vulnerability has been discovered within Hasura GraphQL Engine prior to versions 1.3.4, 2.55.1, 2.20.1, and 2.21.0-beta1. Projects running on Hasura Cloud were not vulnerable. Self-hosted Hasura Projects with deployments that are publicly exposed and not protected by a WAF or other HTTP protection layer should be upgraded to version 1.3.4, 2.55.1, 2.20.1, or 2.21.0-beta1 to receive a patch.

## References
- https://github.com/hasura/graphql-engine/releases/tag/v1.3.4
- https://github.com/hasura/graphql-engine/releases/tag/v2.11.5
- https://github.com/hasura/graphql-engine/releases/tag/v2.20.1
- https://github.com/hasura/graphql-engine/releases/tag/v2.21.0-beta.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27588.json
- https://github.com/hasura/graphql-engine/security/advisories/GHSA-c9rw-rw2f-mj4x
- https://nvd.nist.gov/vuln/detail/CVE-2023-27588
- https://github.com/hasura/graphql-engine/commit/dda54543ee1ecf647ca5d0971b140c3a7b9f4158
