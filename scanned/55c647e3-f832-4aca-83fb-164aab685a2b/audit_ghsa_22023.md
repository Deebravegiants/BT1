# [M] Jenkins View26 Test-Reporting Plugin stores access token in plain text

## Summary
Severity: Medium
Advisory: GHSA-5rc5-4c5c-4cwx
CVE: CVE-2019-10452
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5rc5-4c5c-4cwx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:view26` — affected >=0

## Details
Jenkins View26 Test-Reporting Plugin stores an access token unencrypted in job `config.xml` files on the Jenkins controller. This token can be viewed by users with Extended Read permission or access to the Jenkins controller file system.

As of publication of this advisory there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10452
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1440
