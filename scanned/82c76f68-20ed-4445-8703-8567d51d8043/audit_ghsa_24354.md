# [H] XXE vulnerability in Jenkins Parasoft Findings Plugin

## Summary
Severity: High
Advisory: GHSA-2rh4-xgmq-63jp
CVE: CVE-2020-2178
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2rh4-xgmq-63jp
Type: github-advisory

## Affected
- Maven: `com.parasoft:parasoft-findings` — affected >=0 <10.4.4

## Details
Parasoft Findings Plugin implements a static analysis parser for various Parasoft products and integrates with [Warnings Plugin](https://plugins.jenkins.io/warnings) (10.4.1 and earlier) and [Warnings NG Plugin](https://plugins.jenkins.io/warnings-ng) (10.4.2 and newer).

Parasoft Findings Plugin 10.4.3 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks. This allows a user able to control the input files for the Parasoft Findings parser to have Jenkins parse a crafted file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

Parasoft Findings Plugin 10.4.4 disables external entity resolution for its XML parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2178
- https://github.com/jenkinsci/parasoft-findings-plugin
- https://jenkins.io/security/advisory/2020-04-16/#SECURITY-1753
- http://www.openwall.com/lists/oss-security/2020/04/16/4
