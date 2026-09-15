# [M] Jenkins GitHub Branch Source Plugin allows any user with Overall/Read permission to get list of valid credentials IDs

## Summary
Severity: Medium
Advisory: GHSA-6jp2-hggx-8j7p
CVE: CVE-2017-1000087
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6jp2-hggx-8j7p
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:github-branch-source` — affected >=0 <2.2.0-alpha-1

## Details
GitHub Branch Source provides a list of applicable credential IDs to allow users configuring a job to select the one they'd like to use. This functionality did not check permissions, allowing any user with Overall/Read permission to get a list of valid credentials IDs. Those could be used as part of an attack to capture the credentials using another vulnerability. An enumeration of credentials IDs in this plugin now requires the permission to have Extended Read permission (when that permission is enabled; otherwise Configure permission) to the job in whose context credentials are being accessed. If no job context exists, Overall/Administer permission is required.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000087
- https://github.com/jenkinsci/github-branch-source-plugin
- https://jenkins.io/security/advisory/2017-07-10
