# [H] Jenkins Compuware Common Configuration Plugin vulnerable to Improper Restriction of XML External Entity Reference

## Summary
Severity: High
Advisory: GHSA-g43x-pcc9-f472
CVE: CVE-2022-41226
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-g43x-pcc9-f472
Type: github-advisory

## Affected
- Maven: `com.compuware.jenkins:compuware-common-configuration` — affected >=0 <1.0.15

## Details
Jenkins Compuware Common Configuration Plugin 1.0.14 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers able to change the contents of the Topaz Workbench CLI home directory on agents to have Jenkins parse a crafted file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41226
- https://github.com/jenkinsci/compuware-common-configuration-plugin/pull/24
- https://github.com/jenkinsci/compuware-common-configuration-plugin/commit/351a46798cdc10479cb6966f05a51bc2174806a0
- https://github.com/jenkinsci/compuware-common-configuration-plugin/commit/8410fd5e0a619200f5bc2e906ecba940e8506436
- https://github.com/jenkinsci/compuware-common-configuration-plugin/commit/a92f1fba5ab375cfcceed92a16666a4c709e0f3b
- https://github.com/jenkinsci/compuware-common-configuration-plugin
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2832
