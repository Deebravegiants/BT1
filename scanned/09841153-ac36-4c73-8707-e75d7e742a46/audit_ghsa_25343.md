# [H] XXE vulnerability in Jenkins Liquibase Runner Plugin

## Summary
Severity: High
Advisory: GHSA-xx7g-f287-f9fq
CVE: CVE-2020-2284
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xx7g-f287-f9fq
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:liquibase-runner` — affected >=0 <1.4.7

## Details
Jenkins Liquibase Runner Plugin 1.4.5 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers able to provide Liquibase changesets evaluated by the plugin to have Jenkins parse a crafted XML file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

Jenkins Liquibase Runner Plugin 1.4.7 no longer parses Liquibase changesets.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2284
- https://github.com/jenkinsci/liquibase-runner-plugin
- https://www.jenkins.io/security/advisory/2020-09-23/#SECURITY-1887
- http://www.openwall.com/lists/oss-security/2020/09/23/1
