# [M] SonarQube logs sensitive information

## Summary
Severity: Medium
Advisory: GHSA-hw2c-8xgw-mf57
CVE: CVE-2024-38460
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-16
Source: https://github.com/advisories/GHSA-hw2c-8xgw-mf57
Type: github-advisory

## Affected
- Maven: `org.sonarsource.sonarqube:sonar-web` — affected >=0 <9.9.4

## Details
In SonarQube before 10.4 and 9.9.4 LTA, encrypted values generated using the Settings Encryption feature are potentially exposed in cleartext as part of the URL parameters in the logs (such as SonarQube Access Logs, Proxy Logs, etc).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38460
- https://github.com/SonarSource/sonarqube/commit/48f43d6a3bf9bbd7c9b58eb5cde635572184ad01
- https://community.sonarsource.com/t/sonarqube-ce-10-3-0-leaking-encrypted-values-in-web-server-logs/108187
- https://github.com/SonarSource/sonarqube
- https://sonarsource.atlassian.net/browse/SONAR-21559
