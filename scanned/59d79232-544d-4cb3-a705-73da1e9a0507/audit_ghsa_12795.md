# [M] Path traversal vulnerability in Jenkins PWauth Security Realm Plugin

## Summary
Severity: Medium
Advisory: GHSA-5xpc-c4xv-7w62
CVE: CVE-2023-24449
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-5xpc-c4xv-7w62
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:pwauth` — affected >=0

## Details
Jenkins PWauth Security Realm Plugin 0.4 and earlier does not restrict the names of files in methods implementing form validation, allowing attackers with Overall/Read permission to check for the existence of an attacker-specified file path on the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24449
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2985
