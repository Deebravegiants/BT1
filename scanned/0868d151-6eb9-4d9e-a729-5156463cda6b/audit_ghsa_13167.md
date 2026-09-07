# [M] HTML injection vulnerability in Jenkins AWS CodeCommit Trigger Plugin

## Summary
Severity: Medium
Advisory: GHSA-g4qf-5523-7wvf
CVE: CVE-2023-41944
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-g4qf-5523-7wvf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:aws-codecommit-trigger` — affected >=0

## Details
Jenkins AWS CodeCommit Trigger Plugin 3.0.12 and earlier does not escape the queue name parameter passed to a form validation URL, when rendering an error message, resulting in an HTML injection vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41944
- https://www.jenkins.io/security/advisory/2023-09-06/#SECURITY-3102
- http://www.openwall.com/lists/oss-security/2023/09/06/9
