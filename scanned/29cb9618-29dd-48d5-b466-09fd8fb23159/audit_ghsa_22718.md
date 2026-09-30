# [C] XXE vulnerability in Jenkins Job Import Plugin

## Summary
Severity: Critical
Advisory: GHSA-882r-r8fw-p538
CVE: CVE-2019-1003015
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-882r-r8fw-p538
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:job-import-plugin` — affected >=0 <3.0

## Details
An XML external entity (XXE) processing vulnerability exists in Jenkins Job Import Plugin 2.1 and earlier in src/main/java/org/jenkins/ci/plugins/jobimport/client/RestApiClient.java that allows attackers with the ability to control the HTTP server (Jenkins) queried in preparation of job import to read arbitrary files, perform a denial of service attack, etc.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003015
- https://github.com/jenkinsci/job-import-plugin
- https://jenkins.io/security/advisory/2019-01-28/#SECURITY-905%20(1)
