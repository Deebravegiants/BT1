# [M] Jenkins Sofy.AI Plugin stores API token in plain text 

## Summary
Severity: Medium
Advisory: GHSA-757g-m98v-6r49
CVE: CVE-2019-10447
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-757g-m98v-6r49
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:sofy-ai` — affected >=0

## Details
Jenkins Sofy.AI Plugin stores an API token unencrypted in job config.xml files on the Jenkins controller. This token can be viewed by users with Extended Read permission or access to the Jenkins controller file system.

As of publication of this advisory there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10447
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1431
- http://www.openwall.com/lists/oss-security/2019/10/16/6
