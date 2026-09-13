# [M] Quarkus: authorization flaw in quarkus resteasy reactive and classic

## Summary
Severity: Medium
Advisory: GHSA-25w4-hfqg-4r52
CVE: CVE-2023-5675
CWE: CWE-285, CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-04-25
Source: https://github.com/advisories/GHSA-25w4-hfqg-4r52
Type: github-advisory

## Affected
- Maven: `io.quarkus:quarkus-resteasy-reactive-common-deployment` — affected >=0 <3.2.10.Final
- Maven: `io.quarkus:quarkus-resteasy-reactive-common` — affected >=0 <3.2.10.Final
- Maven: `io.quarkus:quarkus-resteasy-reactive-common-deployment` — affected >=3.3.0 <3.6.9
- Maven: `io.quarkus:quarkus-resteasy-reactive-common` — affected >=3.3.0 <3.6.9
- Maven: `io.quarkus:quarkus-resteasy-reactive-common-deployment` — affected >=3.7.0 <3.7.1
- Maven: `io.quarkus:quarkus-resteasy-reactive-common` — affected >=3.7.0 <3.7.1

## Details
A flaw was found in Quarkus. When a Quarkus RestEasy Classic or Reactive JAX-RS endpoint has its methods declared in the abstract Java class or customized by Quarkus extensions using the annotation processor, the authorization of these methods will not be enforced if it is enabled by either 'quarkus.security.jaxrs.deny-unannotated-endpoints' or 'quarkus.security.jaxrs.default-roles-allowed' properties.

While backports of this fix exist in versions 3.6.9 and 3.7.1 users of older versions are encouraged to update to the 3.8.x LTS branch.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5675
- https://github.com/quarkusio/quarkus/commit/b7dd69a3012a872f2846d73072ff232e07da74dd
- https://github.com/quarkusio/quarkus/commit/bf2ef6c504b989f74ceb5947d823b6ab208f8b6e
- https://github.com/quarkusio/quarkus/commit/c026b1cf6f2e07cc50b65c824d922319248d9341
- https://github.com/quarkusio/quarkus/commit/d802748128cd1932279b7c334f3792d481814ef5
- https://access.redhat.com/errata/RHSA-2024:0494
- https://access.redhat.com/errata/RHSA-2024:0495
- https://access.redhat.com/security/cve/CVE-2023-5675
- https://bugzilla.redhat.com/show_bug.cgi?id=2245197
- https://github.com/quarkusio/quarkus
