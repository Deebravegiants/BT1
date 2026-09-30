# [M] Spring Boot's Mail Auto-Configuration Does Not Enable SSL Hostname Verification

## Summary
Severity: Medium
Advisory: GHSA-9wxp-w4px-32vh
CVE: CVE-2026-40992
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-9wxp-w4px-32vh
Type: github-advisory

## Affected
- Maven: `org.springframework.boot:spring-boot-starter-mail` — affected >=4.0.0 <4.0.7
- Maven: `org.springframework.boot:spring-boot-starter-mail` — affected >=3.5.0 <3.5.15
- Maven: `org.springframework.boot:spring-boot-starter-mail` — affected >=3.4.0

## Details
Spring Boot's Mail auto-configuration does not enable hostname verification. Applications that set the relevant JavaMail property, such as spring.mail.properties.mail.smtp.ssl.checkserveridentity=true, are not affected.

Affected versions:
Spring Boot 4.0.0 through 4.0.6; 3.5.0 through 3.5.14; 3.4.0 through 3.4.16.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40992
- https://github.com/spring-projects/spring-boot
- https://spring.io/security/cve-2026-40992
