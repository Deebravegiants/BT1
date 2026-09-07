# [M] Spring Framework vulnerable to denial of service via specially crafted SpEL expression

## Summary
Severity: Medium
Advisory: GHSA-564r-hj7v-mcr5
CVE: CVE-2023-20861
CWE: CWE-400, CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-23
Source: https://github.com/advisories/GHSA-564r-hj7v-mcr5
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-expression` — affected >=6.0.0 <6.0.7
- Maven: `org.springframework:spring-expression` — affected >=5.3.0 <5.3.26
- Maven: `org.springframework:spring-expression` — affected >=0 <5.2.23.RELEASE

## Details
In Spring Framework versions 6.0.0 - 6.0.6, 5.3.0 - 5.3.25, 5.2.0.RELEASE - 5.2.22.RELEASE, and older unsupported versions, it is possible for a user to provide a specially crafted SpEL expression that may cause a denial-of-service (DoS) condition.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-20861
- https://github.com/spring-projects/spring-framework/commit/430fc25acad2e85cbdddcd52b64481691f03ebd1
- https://github.com/spring-projects/spring-framework/commit/52c93b1c4b24d70de233a958e60e7c5822bd274f
- https://github.com/spring-projects/spring-framework/commit/935c29e3ddba5b19951e54f6685c70ed45d9cbe5
- https://github.com/spring-projects/spring-framework
- https://security.netapp.com/advisory/ntap-20230420-0007
- https://spring.io/security/cve-2023-20861
