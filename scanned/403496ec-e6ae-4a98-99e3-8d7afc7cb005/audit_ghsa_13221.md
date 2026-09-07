# [H] Quarkus HTTP vulnerable to incorrect evaluation of permissions

## Summary
Severity: High
Advisory: GHSA-4f4r-wgv2-jjvg
CVE: CVE-2023-4853
CWE: CWE-148, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-20
Source: https://github.com/advisories/GHSA-4f4r-wgv2-jjvg
Type: github-advisory

## Affected
- Maven: `io.quarkus:quarkus-vertx-http` — affected >=0 <2.16.11.Final
- Maven: `io.quarkus:quarkus-vertx-http` — affected >=3.0.0 <3.2.6.Final
- Maven: `io.quarkus:quarkus-vertx-http` — affected >=3.3.0 <3.3.3
- Maven: `io.quarkus:quarkus-undertow` — affected >=0 <2.16.11.Final
- Maven: `io.quarkus:quarkus-undertow` — affected >=3.0.0 <3.2.6.Final
- Maven: `io.quarkus:quarkus-undertow` — affected >=3.3.0 <3.3.3
- Maven: `io.quarkus:quarkus-csrf-reactive` — affected >=0 <2.16.11.Final
- Maven: `io.quarkus:quarkus-csrf-reactive` — affected >=3.0.0 <3.2.6.Final
- Maven: `io.quarkus:quarkus-csrf-reactive` — affected >=3.3.0 <3.3.3
- Maven: `io.quarkus:quarkus-keycloak-authorization` — affected >=0 <2.16.11.Final
- Maven: `io.quarkus:quarkus-keycloak-authorization` — affected >=3.0.0 <3.2.6.Final
- Maven: `io.quarkus:quarkus-keycloak-authorization` — affected >=3.3.0 <3.3.3

## Details
A flaw was found in Quarkus where HTTP security policies are not sanitizing certain character permutations correctly when accepting requests, resulting in incorrect evaluation of permissions. This issue could allow an attacker to bypass the security policy altogether, resulting in unauthorized endpoint access and possibly a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4853
- https://github.com/quarkusio/quarkus/issues/35785
- https://github.com/quarkusio/quarkus/discussions/35940
- https://github.com/quarkusio/quarkus
- https://bugzilla.redhat.com/show_bug.cgi?id=2238034
- https://access.redhat.com/security/vulnerabilities/RHSB-2023-002
- https://access.redhat.com/security/cve/CVE-2023-4853
- https://access.redhat.com/errata/RHSA-2023:7653
- https://access.redhat.com/errata/RHSA-2023:6112
- https://access.redhat.com/errata/RHSA-2023:6107
- https://access.redhat.com/errata/RHSA-2023:5480
- https://access.redhat.com/errata/RHSA-2023:5479
- https://access.redhat.com/errata/RHSA-2023:5446
- https://access.redhat.com/errata/RHSA-2023:5337
- https://access.redhat.com/errata/RHSA-2023:5310
- https://access.redhat.com/errata/RHSA-2023:5170
- https://access.redhat.com/articles/11258
