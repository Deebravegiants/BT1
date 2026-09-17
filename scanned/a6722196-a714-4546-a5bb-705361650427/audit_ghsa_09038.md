# [H] Jenkins Credentials Binding Plugin does not properly sanitize file names for file and zip file credentials

## Summary
Severity: High
Advisory: GHSA-fxxf-w25w-mcx2
CVE: CVE-2026-48922
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-fxxf-w25w-mcx2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:credentials-binding` — affected >=0 <725.ve52b

## Details
Jenkins Credentials Binding Plugin 720.v3f6decef43ea_ and earlier does not properly sanitize file names for file and zip file credentials.

This allows attackers able to provide credentials to a job to write files to arbitrary locations on the node filesystem. If Jenkins is configured to allow a low-privileged user to configure file or zip file credentials used for a job running on the built-in node, this can lead to remote code execution.

Credentials Binding Plugin 725.ve52b_2328a_fde improves sanitization of the file name provided for file and zip file credentials, preventing path traversal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-48922
- https://github.com/jenkinsci/credentials-binding-plugin
- https://www.jenkins.io/security/advisory/2026-05-27/#SECURITY-3790
