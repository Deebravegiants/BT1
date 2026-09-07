# [M] Stored XSS vulnerability in Jenkins Bitbucket Server Integration Plugin

## Summary
Severity: Medium
Advisory: GHSA-45v7-65q8-x294
CVE: CVE-2022-28133
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-45v7-65q8-x294
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:atlassian-bitbucket-server-integration` — affected >=2.0.0 <3.2.0

## Details
Jenkins Bitbucket Server Integration Plugin 3.1.0 and earlier does not limit URL schemes for callback URLs on OAuth consumers, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to create BitBucket Server consumers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28133
- https://github.com/jenkinsci/atlassian-bitbucket-server-integration-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-2639
- http://www.openwall.com/lists/oss-security/2022/03/29/1
