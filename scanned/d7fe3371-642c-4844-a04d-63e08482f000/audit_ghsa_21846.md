# [M] Improper Limitation of a Pathname to a Restricted Directory in Jenkins Pipeline: Shared Groovy Libraries Plugin

## Summary
Severity: Medium
Advisory: GHSA-5hfv-mg5x-mv32
CVE: CVE-2022-25178
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-5hfv-mg5x-mv32
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.workflow:workflow-cps-global-lib` — affected >=2.22 <561.va_ce0de3c2d69
- Maven: `org.jenkins-ci.plugins.workflow:workflow-cps-global-lib` — affected >=2.19 <2.21.1
- Maven: `org.jenkins-ci.plugins.workflow:workflow-cps-global-lib` — affected >=0 <2.18.1

## Details
Jenkins Pipeline: Shared Groovy Libraries Plugin does not restrict the names of resources passed to the libraryResource step, allowing attackers able to configure Pipelines permission to read arbitrary files on the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25178
- https://github.com/jenkinsci/workflow-cps-global-lib-plugin
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2613
