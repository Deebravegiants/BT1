# [M] Jenkins MathWorks Polyspace Plugin vulnerable to arbitrary file read

## Summary
Severity: Medium
Advisory: GHSA-q6cq-8r4j-6rj5
CVE: CVE-2023-37960
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-q6cq-8r4j-6rj5
Type: github-advisory

## Affected
- Maven: `com.mathworks.polyspace.jenkins:mathworks-polyspace` — affected >=0

## Details
Jenkins MathWorks Polyspace Plugin 1.0.5 and earlier does not restrict the path of the attached files in Polyspace Notification post-build step.

This allows attackers with Item/Configure permission to send emails with arbitrary files from the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37960
- https://www.jenkins.io/security/advisory/2023-07-12/#SECURITY-3124
- http://www.openwall.com/lists/oss-security/2023/07/12/2
