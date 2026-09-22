# [H] Spring Cloud Gateway's SSL bundle configuration silently bypassed

## Summary
Severity: High
Advisory: GHSA-hwqh-2684-54fc
CVE: CVE-2026-22750
CWE: CWE-15
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-hwqh-2684-54fc
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-gateway` — affected >=4.2.0 <4.2.1

## Details
When configuring SSL bundles in Spring Cloud Gateway by using the configuration property spring.ssl.bundle, the configuration was silently ignored and the default SSL configuration was used instead.

Note: The 4.2.x branch is no longer under open source support. If you are using Spring Cloud Gateway 4.2.0 and are not an enterprise customer, you can upgrade to any Spring Cloud Gateway 4.2.x release newer than 4.2.0 available on Maven Centeral https://repo1.maven.org/maven2/org/springframework/cloud/spring-cloud-gateway/ . Ideally, if you are not an enterprise customer, you should be upgrading to 5.0.2 or 5.1.1, which are the current supported open source releases.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22750
- https://github.com/spring-cloud/spring-cloud-gateway/pull/3641
- https://github.com/spring-cloud/spring-cloud-gateway/commit/84009f2ee421e2191f8cc32ce3a84e7fc09e305e
- https://github.com/spring-cloud/spring-cloud-gateway
- https://github.com/spring-cloud/spring-cloud-gateway/releases/tag/v4.2.1
- https://spring.io/security/cve-2026-22750
