# [M] Missing webhook endpoint authorization in Jenkins Rundeck Plugin

## Summary
Severity: Medium
Advisory: GHSA-qgv4-7jhx-c72q
CVE: CVE-2022-41234
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-qgv4-7jhx-c72q
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:rundeck` — affected >=0 <3.6.12

## Details
Jenkins Rundeck Plugin 3.6.11 and earlier does not protect access to the `/plugin/rundeck/webhook/` endpoint, allowing users with Overall/Read permission to trigger jobs that are configured to be triggerable via Rundeck.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41234
- https://github.com/jenkinsci/rundeck-plugin
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2169
