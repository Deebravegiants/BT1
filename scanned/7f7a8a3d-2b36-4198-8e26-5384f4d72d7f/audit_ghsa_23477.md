# [M] XXE vulnerability in Jenkins Visualworks Store Plugin

## Summary
Severity: Medium
Advisory: GHSA-jvjm-j945-8qwc
CVE: CVE-2020-2315
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jvjm-j945-8qwc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:visualworks-store` — affected >=0 <1.1.4

## Details
Jenkins Visualworks Store Plugin 1.1.3 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers with the ability to control the output of a script that run Visualworks with StoreCI, or able to control an agent process, to have Jenkins parse a crafted file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

Jenkins Visualworks Store Plugin 1.1.4 disables external entity resolution for its XML parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2315
- https://github.com/jenkinsci/visualworks-store-plugin/commit/267bb709c3412f6517b4631c867d16eb72af6d69
- https://github.com/jenkinsci/visualworks-store-plugin
- https://www.jenkins.io/security/advisory/2020-11-04/#SECURITY-1900
