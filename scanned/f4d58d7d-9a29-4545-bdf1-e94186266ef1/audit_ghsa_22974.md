# [M] Jenkins Deploy to container Plugin stored plain text passwords in job configuration

## Summary
Severity: Medium
Advisory: GHSA-3q6p-r6rr-266x
CVE: CVE-2017-1000113
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-3q6p-r6rr-266x
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:deploy` — affected >=0 <1.13

## Details
The Deploy to container Plugin stored passwords unencrypted as part of its configuration. This allowed users with Jenkins master local file system access, or users with Extended Read access to the jobs it is used in, to retrieve those passwords. The Deploy to container Plugin now integrates with Credentials Plugin to store passwords securely, and automatically migrates existing passwords.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000113
- https://jenkins.io/security/advisory/2017-08-07
