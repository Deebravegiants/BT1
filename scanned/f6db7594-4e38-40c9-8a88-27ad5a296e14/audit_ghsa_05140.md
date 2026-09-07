# [H] Spring for Apache Pulsar: JsonPulsarHeaderMapper Trusted-Package Prefix Check Allows Unintended Subpackage Deserialization

## Summary
Severity: High
Advisory: GHSA-gg69-9wwp-6jx2
CVE: CVE-2026-41732
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-gg69-9wwp-6jx2
Type: github-advisory

## Affected
- Maven: `org.springframework.pulsar:spring-pulsar` — affected >=2.0.0 <2.0.6
- Maven: `org.springframework.pulsar:spring-pulsar` — affected >=1.2.0 <1.2.18
- Maven: `org.springframework.pulsar:spring-pulsar` — affected >=0

## Details
JsonPulsarHeaderMapper matched type headers against trusted packages using a prefix check, meaning that trusting any package implicitly trusted all of its subpackages. Additionally, an empty trusted-packages configuration fell back to trusting all packages rather than applying a safe default allow-list.

Affected versions:
Spring for Apache Pulsar 2.0.0 through 2.0.5; 1.2.0 through 1.2.17; 1.1.0 through 1.1.17.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41732
- https://github.com/spring-projects/spring-pulsar
- https://github.com/spring-projects/spring-pulsar/releases/tag/v1.2.18
- https://github.com/spring-projects/spring-pulsar/releases/tag/v2.0.6
- https://spring.io/security/cve-2026-41732
