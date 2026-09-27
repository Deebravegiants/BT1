# [M] Jenkins Sidebar Link Plugin vulnerable to Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-pp8m-prr7-wr8w
CVE: CVE-2023-32985
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-pp8m-prr7-wr8w
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:sidebar-link` — affected >=0 <2.2.2

## Details
Jenkins Sidebar Link Plugin allows specifying files in the `userContent/` directory for use as link icons.

Sidebar Link Plugin 2.2.1 and earlier does not restrict the path of files in a method implementing form validation.

This allows attackers with Overall/Read permission to check for the existence of an attacker-specified file path on the Jenkins controller file system.

Sidebar Link Plugin 2.2.2 ensures that only files located within the expected `userContent/` directory can be accessed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32985
- https://github.com/jenkinsci/sidebar-link-plugin/commit/1bfd878ee107cdf349bc6a6bf3e9e6e25ef95ad5
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-3125
