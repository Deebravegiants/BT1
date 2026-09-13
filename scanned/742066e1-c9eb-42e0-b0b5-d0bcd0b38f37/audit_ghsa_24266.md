# [M] XXE vulnerability in Jenkins pom2config Plugin

## Summary
Severity: Medium
Advisory: GHSA-ppv9-v43c-xqpp
CVE: CVE-2021-43576
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-ppv9-v43c-xqpp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:pom2config` — affected >=0

## Details
Jenkins pom2config Plugin 1.2 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers with Overall/Read and Item/Read permissions to have Jenkins parse a crafted XML file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43576
- https://github.com/jenkinsci/pom2config-plugin
- https://www.jenkins.io/security/advisory/2021-11-12/#SECURITY-2415
- https://www.zerodayinitiative.com/advisories/ZDI-21-1314
- http://www.openwall.com/lists/oss-security/2021/11/12/1
