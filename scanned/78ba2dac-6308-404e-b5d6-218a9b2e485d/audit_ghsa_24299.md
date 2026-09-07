# [M] Stored XSS vulnerability in Jenkins S3 Publisher Plugin

## Summary
Severity: Medium
Advisory: GHSA-3892-qqv6-h2qm
CVE: CVE-2018-1000177
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-3892-qqv6-h2qm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:s3` — affected >=0 <0.11.0

## Details
A cross-site scripting vulnerability exists in Jenkins S3 Plugin 0.10.12 and older in src/main/resources/hudson/plugins/s3/S3ArtifactsProjectAction/jobMain.jelly that allows attackers able to control file names of uploaded files to define file names containing JavaScript that would be executed in another user's browser when that user performs some UI actions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000177
- https://jenkins.io/security/advisory/2018-04-16
