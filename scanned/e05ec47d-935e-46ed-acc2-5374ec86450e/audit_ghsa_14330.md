# [H] Jenkins Cppcheck Plugin vulnerable to stored cross-site scripting (XSS)

## Summary
Severity: High
Advisory: GHSA-j927-269r-96xw
CVE: CVE-2023-28678
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-02
Source: https://github.com/advisories/GHSA-j927-269r-96xw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cppcheck` — affected >=0

## Details
Jenkins Cppcheck Plugin 1.26 and earlier does not escape file names from Cppcheck report files before showing them on the Jenkins UI.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to control report file contents.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28678
- https://github.com/jenkinsci/cppcheck-plugin
- https://www.jenkins.io/security/advisory/2023-03-21/#SECURITY-2809
