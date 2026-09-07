# [H] XXE vulnerability in Jenkins Cobertura Plugin

## Summary
Severity: High
Advisory: GHSA-vpfj-5gg5-fvfm
CVE: CVE-2020-2138
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vpfj-5gg5-fvfm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cobertura` — affected >=0 <1.16

## Details
Cobertura Plugin 1.15 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows a user able to control the input files for the 'Publish Cobertura Coverage Report' post-build step to have Jenkins parse a crafted file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

Cobertura Plugin 1.16 disables external entity resolution for its XML parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2138
- https://github.com/jenkinsci/cobertura-plugin/commit/fdee535fe4782181d822b875c96df8306f245d48
- https://github.com/jenkinsci/cobertura-plugin
- https://jenkins.io/security/advisory/2020-03-09/#SECURITY-1700
- http://www.openwall.com/lists/oss-security/2020/03/09/1
