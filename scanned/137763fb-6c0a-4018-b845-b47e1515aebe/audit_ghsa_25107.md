# [M] Jenkins Job Import Plugin CSRF vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8crr-xf35-5f5p
CVE: CVE-2019-1003017
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8crr-xf35-5f5p
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:job-import-plugin` — affected >=0 <3.1

## Details
A data modification vulnerability exists in Jenkins Job Import Plugin 3.0 and earlier in JobImportAction.java that allows attackers to copy jobs from a preconfigured other Jenkins instance, potentially installing additional plugins necessary to load the imported job's configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003017
- https://github.com/jenkinsci/job-import-plugin/commit/8f826a684ba0969697d2a92a6f448aef8f03b66c
- https://github.com/jenkinsci/job-import-plugin
- https://jenkins.io/security/advisory/2019-01-28/#SECURITY-1302
