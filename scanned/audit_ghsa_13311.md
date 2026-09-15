# [H] Spring-boot-admin sandbox bypass via crafted HTML

## Summary
Severity: High
Advisory: GHSA-7gj7-224w-vpr3
CVE: CVE-2023-38286
CWE: CWE-77
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-14
Source: https://github.com/advisories/GHSA-7gj7-224w-vpr3
Type: github-advisory

## Affected
- Maven: `de.codecentric:spring-boot-admin-server` — affected >=3.0.0 <3.1.2
- Maven: `de.codecentric:spring-boot-admin-server` — affected >=0 <2.7.16

## Details
Thymeleaf through 3.1.1.RELEASE as used in spring-boot-admin (aka Spring Boot Admin) through 3.1.1 allows for a sandbox bypass via crafted HTML. This may be relevant for SSTI (Server Side Template Injection) and code execution in spring-boot-admin if MailNotifier is enabled and there is write access to environment variables via the UI.

Spring Boot Admin 3.1.2 and 2.7.16 contain mitigations for the issue. This bypass is achived via a library called Thymeleaf which has added counter measures for this sort of bypass in version `3.1.2.RELEASE` which has explicity forbidden static access to `org.springframework.util` in expressions. Thymeleaf itself should not be considered vulnerable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-38286
- https://github.com/codecentric/spring-boot-admin/issues/2613
- https://github.com/thymeleaf/thymeleaf/issues/966
- https://github.com/codecentric/spring-boot-admin/pull/2615
- https://github.com/codecentric/spring-boot-admin/commit/f1f6ac6f613e1c0afc121c8989f28b4155a6797a
- https://github.com/codecentric/spring-boot-admin/commit/f1f6ac6f613e1c0afc121c8989f28b4155a6797a#diff-1ea8b144c29588e08221597d56d8be10b4b4a210f248a83f2e837152a3d2e0d7
- https://github.com/codecentric/spring-boot-admin
- https://github.com/codecentric/spring-boot-admin/blob/master/spring-boot-admin-server/pom.xml
- https://github.com/p1n93r/SpringBootAdmin-thymeleaf-SSTI
