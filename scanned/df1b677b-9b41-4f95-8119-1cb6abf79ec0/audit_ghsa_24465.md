# [H] Jenkins SonarQube Scanner Plugin stored server authentication token in plain text

## Summary
Severity: High
Advisory: GHSA-3ccq-gccx-pm7j
CVE: CVE-2018-1000425
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3ccq-gccx-pm7j
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:sonar` — affected >=0 <2.8.1

## Details
An insufficiently protected credentials vulnerability exists in Jenkins SonarQube Scanner Plugin 2.8 and earlier in SonarInstallation.java that allows attackers with local file system access to obtain the credentials used to connect to SonarQube.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000425
- https://jenkins.io/security/advisory/2018-09-25/#SECURITY-1163
- http://www.securityfocus.com/bid/106532
