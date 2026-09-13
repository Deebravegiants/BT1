# [H] Spring Boot DevTools remote secret comparison is vulnerable to timing attacks

## Summary
Severity: High
Advisory: GHSA-56v8-86gj-66jp
CVE: CVE-2026-40972
CWE: CWE-208
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-56v8-86gj-66jp
Type: github-advisory

## Affected
- Maven: `org.springframework.boot:spring-boot-devtools` — affected >=4.0.0 <4.0.6
- Maven: `org.springframework.boot:spring-boot-devtools` — affected >=3.5.0 <3.5.14
- Maven: `org.springframework.boot:spring-boot-devtools` — affected >=3.4.0
- Maven: `org.springframework.boot:spring-boot-devtools` — affected >=3.3.0
- Maven: `org.springframework.boot:spring-boot-devtools` — affected >=0

## Details
An attacker on the same network as the remote application may be able to utilize a timing attack to discover information about the remote secret. In extreme circumstances this could result in the attacker determining the secret and uploading changed classes, thereby achieving remote code execution in the remote application.

Affected: Spring Boot 4.0.0–4.0.5 (fix 4.0.6), 3.5.0–3.5.13 (fix 3.5.14), 3.4.0–3.4.15 (fix 3.4.16), 3.3.0–3.3.18 (fix 3.3.19), 2.7.0–2.7.32 (fix 2.7.33); DevTools remote secret comparison. Versions that are no longer supported are also affected per vendor advisory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40972
- https://github.com/spring-projects/spring-boot
- https://spring.io/security/cve-2026-40972
