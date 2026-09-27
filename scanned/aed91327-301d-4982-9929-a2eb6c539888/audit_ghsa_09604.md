# [H] Spring Boot accepts predictable temp directory without ownership verification

## Summary
Severity: High
Advisory: GHSA-wwpq-f5c3-7hvx
CVE: CVE-2026-40973
CWE: CWE-377
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-wwpq-f5c3-7hvx
Type: github-advisory

## Affected
- Maven: `org.springframework.boot:spring-boot` — affected >=4.0.0 <4.0.6
- Maven: `org.springframework.boot:spring-boot` — affected >=3.5.0 <3.5.14
- Maven: `org.springframework.boot:spring-boot` — affected >=3.4.0
- Maven: `org.springframework.boot:spring-boot` — affected >=3.3.0
- Maven: `org.springframework.boot:spring-boot` — affected >=0

## Details
A local attacker on the same host as the application may be able to take control of the directory used by `ApplicationTemp`. When `server.servlet.session.persistent` is set to `true` and the attack persists across application restarts, this may allow the attacker to read session information and hijack authenticated users or deploy a gadget chain and execute code as the application's user.

Affected: Spring Boot 4.0.0–4.0.5 (fix 4.0.6), 3.5.0–3.5.13 (fix 3.5.14), 3.4.0–3.4.15 (fix 3.4.16), 3.3.0–3.3.18 (fix 3.3.19), 2.7.0–2.7.32 (fix 2.7.33); predictable temp directory / `ApplicationTemp` ownership verification. Versions that are no longer supported are also affected per vendor advisory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40973
- https://github.com/spring-projects/spring-boot
- https://spring.io/security/cve-2026-40973
