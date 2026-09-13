# [M] Spring Security's spring-security.xsd file is world writable

## Summary
Severity: Medium
Advisory: GHSA-9gp8-6cg8-7h34
CVE: CVE-2023-34042
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-02-06
Source: https://github.com/advisories/GHSA-9gp8-6cg8-7h34
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-config` — affected >=6.1.1 <6.1.4
- Maven: `org.springframework.security:spring-security-config` — affected >=6.0.4 <6.0.7
- Maven: `org.springframework.security:spring-security-config` — affected >=5.8.4 <5.8.7
- Maven: `org.springframework.security:spring-security-config` — affected >=5.7.9 <5.7.11

## Details
The spring-security.xsd file inside the spring-security-config jar is world writable which means that if it were extracted it could be written by anyone with access to the file system.

While there are no known exploits, this is an example of “CWE-732: Incorrect Permission Assignment for Critical Resource” and could result in an exploit. Users should update to the latest version of Spring Security to mitigate any future exploits found around this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34042
- https://github.com/spring-projects/spring-security/commit/5b293d21161e946bf241d9e974b9af93cfafaaac
- https://github.com/spring-projects/spring-security
- https://security.netapp.com/advisory/ntap-20241129-0010
- https://spring.io/security/cve-2023-34042
