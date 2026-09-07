# [H] Spring Boot Admins integrated notifier support allows arbitrary code execution

## Summary
Severity: High
Advisory: GHSA-w3x5-427h-wfq6
CVE: CVE-2022-46166
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-09
Source: https://github.com/advisories/GHSA-w3x5-427h-wfq6
Type: github-advisory

## Affected
- Maven: `de.codecentric:spring-boot-admin` — affected >=0 <2.6.10
- Maven: `de.codecentric:spring-boot-admin` — affected >=2.7.0 <2.7.8
- Maven: `de.codecentric:spring-boot-admin` — affected >=3.0.0-M1 <3.0.0-M6

## Details
### Impact
All users who run Spring Boot Admin Server, having enabled Notifiers (e.g. Teams-Notifier) and write access to environment variables via UI are possibly affected.

### Patches
In the most recent releases of Spring Boot Admin 2.6.10 and 2.7.8 the issue is fixed by implementing `SimpleExecutionContext` of SpEL. This prevents the arbitrary code execution (i.e. SpEL injection).

### Workarounds
 * Disable any notifier
 * Disable write access (POST request) on `/env` actuator endpoint

## References
- https://github.com/codecentric/spring-boot-admin/security/advisories/GHSA-w3x5-427h-wfq6
- https://github.com/codecentric/spring-boot-admin
