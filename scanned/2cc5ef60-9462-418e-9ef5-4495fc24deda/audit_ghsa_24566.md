# [H] Cross-site Scripting in Jenkins Rundeck Plugin

## Summary
Severity: High
Advisory: GHSA-4m42-8qfq-h3q9
CVE: CVE-2022-30956
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-18
Source: https://github.com/advisories/GHSA-4m42-8qfq-h3q9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:rundeck` — affected >=0 <3.6.11

## Details
Jenkins Rundeck Plugin 3.6.10 and earlier does not restrict URL schemes in Rundeck webhook submissions, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to submit crafted Rundeck webhook payloads. Rundeck Plugin 3.6.11 sanitizes URLs submitted in Rundeck webhook payloads.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30956
- https://github.com/jenkinsci/rundeck-plugin
- https://www.jenkins.io/security/advisory/2022-05-17/#SECURITY-2600
