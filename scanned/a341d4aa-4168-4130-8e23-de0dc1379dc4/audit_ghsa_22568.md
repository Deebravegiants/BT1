# [H] Improper Authentication in Spring Security

## Summary
Severity: High
Advisory: GHSA-gv9v-c375-hvmg
CVE: CVE-2014-0097
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-gv9v-c375-hvmg
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=3.2.0 <3.2.2.RELEASE
- Maven: `org.springframework.security:spring-security-core` — affected >=3.1.0 <3.1.5.RELEASE

## Details
The ActiveDirectoryLdapAuthenticator in Spring Security 3.2.0 to 3.2.1 and 3.1.0 to 3.1.5 does not check the password length. If the directory allows anonymous binds then it may incorrectly authenticate a user who supplies an empty password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0097
- https://github.com/spring-projects/spring-security/commit/7dbb8e777ece8675f3333a1ef1cb4d6b9be80395
- https://github.com/spring-projects/spring-security/commit/88559882e967085c47a7e1dcbc4dc32c2c796868
- https://github.com/spring-projects/spring-security/commit/a7005bd74241ac8e2e7b38ae31bc4b0f641ef973
- https://jira.springsource.org/browse/SEC-2500
- https://pivotal.io/security/cve-2014-0097
- https://www.oracle.com/security-alerts/cpuapr2022.html
