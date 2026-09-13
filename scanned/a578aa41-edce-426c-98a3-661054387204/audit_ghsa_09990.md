# [H] Jenkins Credentials Binding Plugin has a path traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-p2rf-wpxj-mx2g
CVE: CVE-2026-42520
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-p2rf-wpxj-mx2g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:credentials-binding` — affected >=0 <720.v3f6decef43ea

## Details
Jenkins Credentials Binding Plugin versions 719.v80e905ef14eb_ and earlier do not sanitize file names for file and zip file credentials.

This allows attackers able to provide credentials to a job to write files to arbitrary locations on the node filesystem. If Jenkins is configured to allow a low-privileged user to configure file or zip file credentials used for a job running on the built-in node, this can lead to remote code execution.

Credentials Binding Plugin 720.v3f6decef43ea_ sanitizes the file name provided for file and zip file credentials, preventing path traversal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42520
- https://github.com/jenkinsci/credentials-binding-plugin
- https://www.jenkins.io/security/advisory/2026-04-29/#SECURITY-3672
