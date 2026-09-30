# [H] Privilege Escalation via Dropped Field-Level @authentication

## Summary
Severity: High
Advisory: CVE-2026-19869
Aliases: GHSA-82m8-p9px-c3x5
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-19869
Type: osv

## Details
@neo4j/graphql from 5.2.0 until the patched versions fails to enforce field-level @authentication rules on root custom-resolver fields when a type-level @authentication rule is also present on the same operation type. When both a type-level @authentication (on Query/Mutation) and a field-level @authentication (on a root custom-resolver field within that type) are declared, only the type-level rule is evaluated and the field-level rule is silently discarded. As a result a stricter per-field requirement — such as an admin-role JWT claim (jwt: { roles_INCLUDES: "admin" }) — is never checked, and any client that satisfies the coarser type-level requirement can invoke the more-restricted field. No token forgery is involved: a legitimately issued, correctly signed non-admin token (e.g. roles: ["user"]) is sufficient.

## References
- https://registry.npmjs.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19869.json
- https://github.com/neo4j/graphql/security/advisories/GHSA-82m8-p9px-c3x5
- https://neo4j.com/security/CVE-2026-19869
- https://nvd.nist.gov/vuln/detail/CVE-2026-19869
- https://github.com/neo4j/graphql
