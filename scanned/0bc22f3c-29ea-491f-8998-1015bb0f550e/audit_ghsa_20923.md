# [M] Path traversal in Jenkins build-publisher Plugin

## Summary
Severity: Medium
Advisory: GHSA-jrqh-c9v8-ccx9
CVE: CVE-2022-41231
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-jrqh-c9v8-ccx9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:build-publisher` — affected >=0

## Details
Jenkins Build-Publisher Plugin 1.22 and earlier allows attackers with Item/Configure permission to create or replace any `config.xml` file on the Jenkins controller file system by providing a crafted file name to an API endpoint. Additionally, this endpoint does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability that allows attackers to replace any `config.xml` file on the Jenkins controller file system with an empty file.

There is currently no known workaround or fix, and this plugin has been suspended.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41231
- https://github.com/jenkins-infra/update-center2/pull/644
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2139
