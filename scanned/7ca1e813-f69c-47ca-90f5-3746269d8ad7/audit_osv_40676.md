# [M] Subscription Authentication Bypass via Unverified connectionParams.jwt

## Summary
Severity: Medium
Advisory: CVE-2026-5423
Aliases: GHSA-fcpg-3fw5-vc65
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-5423
Type: osv

## Details
@neo4j/graphql library versions prior to 7.5.6 fail to verify the authenticity of a client-supplied, pre-decoded JWT object passed through GraphQL subscription connectionParams. As a result, any unauthenticated remote client that can open a GraphQL-over-WebSocket connection can forge arbitrary JWT claims (e.g. sub, roles) in connectionParams.jwt and have them accepted as authenticated identity for the purposes of @authentication and @subscriptionsAuthorization directive evaluation. This allows a fully unauthenticated attacker to receive subscription events that should be restricted to specific authenticated roles/users.
Upgrade the library to versions 7.5.6+ or 5.12.14+. v6 is end-of-life and will not receive a fix.

## References
- https://registry.npmjs.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5423.json
- https://github.com/neo4j/graphql/security/advisories/GHSA-fcpg-3fw5-vc65
- https://neo4j.com/security/CVE-2026-5423
- https://nvd.nist.gov/vuln/detail/CVE-2026-5423
- https://github.com/neo4j/graphql
