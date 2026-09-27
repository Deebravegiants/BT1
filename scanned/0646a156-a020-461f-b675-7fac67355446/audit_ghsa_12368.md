# [H] Authorization bypass in Quarkus

## Summary
Severity: High
Advisory: GHSA-mvc8-6ffp-jrx5
CVE: CVE-2023-6394
CWE: CWE-551, CWE-696, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-12-09
Source: https://github.com/advisories/GHSA-mvc8-6ffp-jrx5
Type: github-advisory

## Affected
- Maven: `io.quarkus:quarkus-smallrye-graphql-client` — affected >=2.14.0 <3.5.3
- Maven: `io.quarkus:quarkus-smallrye-graphql-client` — affected >=0 <2.13.9.Final

## Details
A flaw was found in Quarkus. This issue occurs when receiving a request over websocket with no role-based permission specified on the GraphQL operation, Quarkus processes the request without authentication despite the endpoint being secured. This can allow an attacker to access information and functionality outside of normal granted API permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6394
- https://github.com/quarkusio/quarkus/pull/36961
- https://access.redhat.com/errata/RHSA-2023:7612
- https://access.redhat.com/errata/RHSA-2023:7700
- https://access.redhat.com/security/cve/CVE-2023-6394
- https://bugzilla.redhat.com/show_bug.cgi?id=2252197
- https://github.com/quarkusio/quarkus
- https://github.com/quarkusio/quarkus/releases/tag/2.13.9.Final
- https://github.com/quarkusio/quarkus/releases/tag/3.5.3
