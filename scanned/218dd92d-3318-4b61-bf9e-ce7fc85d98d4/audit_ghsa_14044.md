# [M] Jenkins Email Extension Plugin missing permission check

## Summary
Severity: Medium
Advisory: GHSA-6gp4-2f92-j2w5
CVE: CVE-2023-32979
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-6gp4-2f92-j2w5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:email-ext` — affected >=0 <2.96.1

## Details
Jenkins Email Extension Plugin 2.96 and earlier does not perform a permission check in a method implementing form validation.

This allows attackers with Overall/Read permission to check for the existence of files in the `email-templates/` directory in the Jenkins home directory on the controller file system.

This form validation method requires the appropriate permission in Email Extension Plugin 2.96.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32979
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-3088%20(1)
