# [H] Spring Security SAML2 Service Provider is vulnerable to Deserialization of Untrusted Data via JdbcAssertingPartyMetadataRepository

## Summary
Severity: High
Advisory: GHSA-2q7c-5gjm-7q23
CVE: CVE-2026-40993
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:H/PR:H/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-2q7c-5gjm-7q23
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-saml2-service-provider` — affected >=7.0.0 <7.0.6

## Details
An attacker with write permissions to the database table managed by JdbcAssertingPartyMetadataRepository (saml2_asserting_party_metadata) may be able to store malicious serialized payloads in the columns containing the collection of verification or encryption credentials (verification_credentials and encryption_credentials, respectively).

Affected versions:
Spring Security 7.0.0 through 7.0.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40993
- https://github.com/spring-projects/spring-security
- https://github.com/spring-projects/spring-security/releases/tag/7.0.6
- https://spring.io/security/cve-2026-40993
