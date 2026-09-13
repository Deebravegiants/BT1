# [M] Quarkus: security checks in resteasy reactive may trigger a denial of service

## Summary
Severity: Medium
Advisory: GHSA-mv64-86g8-cqq7
CVE: CVE-2024-1726
CWE: CWE-281
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-04-25
Source: https://github.com/advisories/GHSA-mv64-86g8-cqq7
Type: github-advisory

## Affected
- Maven: `io.quarkus.resteasy.reactive:resteasy-reactive` — affected >=3.8.0.CR1 <3.8.0
- Maven: `io.quarkus.resteasy.reactive:resteasy-reactive` — affected >=3.3.0.CR1 <3.7.4
- Maven: `io.quarkus.resteasy.reactive:resteasy-reactive` — affected >=0 <3.2.11.Final

## Details
A flaw was discovered in the RESTEasy Reactive implementation in Quarkus. Due to security checks for some JAX-RS endpoints being performed after serialization, more processing resources are consumed while the HTTP request is checked. In certain configurations, if an attacker has knowledge of any POST, PUT, or PATCH request paths, they can potentially identify vulnerable endpoints and trigger excessive resource usage as the endpoints process the requests. This can result in a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1726
- https://github.com/quarkusio/quarkus/commit/34c1a63baf5401d0d578a23a1a4deb4b841ce65b
- https://github.com/quarkusio/quarkus/commit/96d93427f3b4a7d3cff34d8b7b883e13cecd359c
- https://access.redhat.com/errata/RHSA-2024:1662
- https://access.redhat.com/security/cve/CVE-2024-1726
- https://bugzilla.redhat.com/show_bug.cgi?id=2265158
- https://github.com/quarkusio/quarkus
