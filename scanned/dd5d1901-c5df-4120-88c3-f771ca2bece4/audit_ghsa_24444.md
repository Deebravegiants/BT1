# [M] Arbitrary file read vulnerability in Copy data to workspace Jenkins Plugin

## Summary
Severity: Medium
Advisory: GHSA-2f4c-8rp6-fh6q
CVE: CVE-2020-2275
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2f4c-8rp6-fh6q
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:copy-data-to-workspace-plugin` — affected >=0

## Details
Jenkins Copy data to workspace Plugin 1.0 and earlier does not limit which directories can be copied from the Jenkins controller to job workspaces, allowing attackers with Job/Configure permission to read arbitrary files on the Jenkins controller.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2275
- https://github.com/jenkinsci/copy-data-to-workspace-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1966
- http://www.openwall.com/lists/oss-security/2020/09/16/3
