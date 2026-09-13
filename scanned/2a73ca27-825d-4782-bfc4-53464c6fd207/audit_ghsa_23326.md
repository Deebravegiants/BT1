# [H] Improper Restriction of XML External Entity Reference Jenkins Token Macro Plugin

## Summary
Severity: High
Advisory: GHSA-g6h2-4x64-c59x
CVE: CVE-2019-10337
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-g6h2-4x64-c59x
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:token-macro` — affected >=0 <2.8

## Details
An XML external entities (XXE) vulnerability in Jenkins Token Macro Plugin 2.7 and earlier allowed attackers able to control a the content of the input file for the "XML" macro to have Jenkins resolve external entities, resulting in the extraction of secrets from the Jenkins agent, server-side request forgery, or denial-of-service attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10337
- https://github.com/jenkinsci/token-macro-plugin/commit/004319f1b6e2a0f097a096b9df9dc19a5ac0d9b0
- https://access.redhat.com/errata/RHSA-2019:1636
- https://access.redhat.com/errata/RHSA-2019:1851
- https://github.com/jenkinsci/token-macro-plugin
- https://jenkins.io/security/advisory/2019-06-11/#SECURITY-1399
- http://www.openwall.com/lists/oss-security/2019/06/11/1
- http://www.securityfocus.com/bid/108747
