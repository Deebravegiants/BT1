# [M] Jenkins SonarQube Plugin Stores Passwords in Cleartext

## Summary
Severity: Medium
Advisory: GHSA-3x9h-3p7m-33m7
CVE: CVE-2013-5676
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-3x9h-3p7m-33m7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:sonar` — affected >=0

## Details
The Jenkins Plugin for SonarQube 3.7 and earlier allows remote authenticated users to obtain sensitive information (cleartext passwords) by reading the value in the sonar.sonarPassword parameter from jenkins/configure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-5676
- https://github.com/jenkinsci/sonarqube-plugin
- http://seclists.org/fulldisclosure/2013/Dec/37
