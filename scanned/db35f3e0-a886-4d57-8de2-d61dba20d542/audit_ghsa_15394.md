# [H] Signature forgery in Spring Boot's Loader

## Summary
Severity: High
Advisory: GHSA-7cj3-x93g-gj76
CVE: CVE-2024-38807
CWE: CWE-290, CWE-347
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-08-23
Source: https://github.com/advisories/GHSA-7cj3-x93g-gj76
Type: github-advisory

## Affected
- Maven: `org.springframework.boot:spring-boot-loader` — affected >=2.7.0 <2.7.22
- Maven: `org.springframework.boot:spring-boot-loader-classic` — affected >=2.7.0 <2.7.22
- Maven: `org.springframework.boot:spring-boot-loader` — affected >=3.0.0 <3.0.17
- Maven: `org.springframework.boot:spring-boot-loader-classic` — affected >=3.0.0 <3.0.17
- Maven: `org.springframework.boot:spring-boot-loader` — affected >=3.1.0 <3.1.13
- Maven: `org.springframework.boot:spring-boot-loader-classic` — affected >=3.1.0 <3.1.13
- Maven: `org.springframework.boot:spring-boot-loader` — affected >=3.2.0 <3.2.9
- Maven: `org.springframework.boot:spring-boot-loader-classic` — affected >=3.2.0 <3.2.9
- Maven: `org.springframework.boot:spring-boot-loader` — affected >=3.3.0 <3.3.3
- Maven: `org.springframework.boot:spring-boot-loader-classic` — affected >=3.3.0 <3.3.3

## Details
Applications that use spring-boot-loader or spring-boot-loader-classic and contain custom code that performs signature verification of nested jar files may be vulnerable to signature forgery where content that appears to have been signed by one signer has, in fact, been signed by another.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38807
- https://github.com/spring-projects/spring-boot
- https://security.netapp.com/advisory/ntap-20250117-0006
- https://spring.io/security/cve-2024-38807
