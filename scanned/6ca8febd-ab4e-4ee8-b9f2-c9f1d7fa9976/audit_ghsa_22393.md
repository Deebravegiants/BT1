# [H] XXE vulnerability in Jenkins Nested View Plugin

## Summary
Severity: High
Advisory: GHSA-5wc4-w63v-97c3
CVE: CVE-2021-21680
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5wc4-w63v-97c3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:nested-view` — affected >=0 <1.21

## Details
Jenkins Nested View Plugin 1.20 and earlier does not configure its XML transformer to prevent XML external entity (XXE) attacks.

This allows attackers able to configure views to have Jenkins parse a crafted view XML definition that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

Jenkins Nested View Plugin 1.21 disables external entity resolution for its XML transformer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21680
- https://github.com/jenkinsci/nested-view-plugin/commit/79787294f034b3009c3de557c6441c9ceba936b8
- https://github.com/jenkinsci/nested-view-plugin
- https://www.jenkins.io/security/advisory/2021-08-31/#SECURITY-2411
- http://www.openwall.com/lists/oss-security/2021/08/31/1
