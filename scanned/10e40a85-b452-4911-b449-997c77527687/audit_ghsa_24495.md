# [M] Exposure of Sensitive Information to an Unauthorized Actor in SonarSource SonarQube API

## Summary
Severity: Medium
Advisory: GHSA-m643-2pfv-xwm8
CVE: CVE-2018-19413
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-m643-2pfv-xwm8
Type: github-advisory

## Affected
- Maven: `org.sonarsource.sonarqube:sonar-plugin-api` — affected >=0 <7.5

## Details
A vulnerability in the API of SonarSource SonarQube before 7.5 could allow an authenticated user to discover sensitive information such as valid user-account logins in the web application. The vulnerability occurs because of improperly configured access controls that cause the API to return the externalIdentity field to non-administrator users. The attacker could use this information in subsequent attacks against the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19413
- https://github.com/SonarSource/sonarqube/commit/7b567ba3d15ed7dd0b0bba0330686487e35af85c
- https://jira.sonarsource.com/browse/SONAR-11305
- http://packetstormsecurity.com/files/150496/SonarSource-SonarQube-7.3-Information-Disclosure.html
