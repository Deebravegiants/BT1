# [M] XXE vulnerability in Jenkins Performance Plugin

## Summary
Severity: Medium
Advisory: GHSA-hr8p-76q8-fxwq
CVE: CVE-2021-21701
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hr8p-76q8-fxwq
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:performance` — affected >=0

## Details
Jenkins Performance Plugin 3.20 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers able to control workspace contents to have Jenkins parse a crafted XML report file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21701
- https://github.com/jenkinsci/performance-plugin
- https://www.jenkins.io/security/advisory/2021-11-12/#SECURITY-2394
- https://www.zerodayinitiative.com/advisories/ZDI-21-1313
- http://www.openwall.com/lists/oss-security/2021/11/12/1
