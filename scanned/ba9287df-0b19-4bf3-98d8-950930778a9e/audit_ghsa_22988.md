# [H] Jenkins Zulip Plugin vulnerable to Insufficiently Protected Credentials

## Summary
Severity: High
Advisory: GHSA-hfjr-m75m-wmh7
CVE: CVE-2019-10476
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hfjr-m75m-wmh7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:zulip` — affected >=0 <1.1.1

## Details
Jenkins Zulip Plugin prior to 1.1.1 stored credentials unencrypted in its global configuration file on the Jenkins master where they could be viewed by users with access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10476
- https://github.com/jenkinsci/zulip-plugin/commit/2a9dd6c41c2d913b0414d015b3118e3ddb60bd90
- https://github.com/jenkinsci/zulip-plugin
- https://github.com/jenkinsci/zulip-plugin/releases/tag/1.1.1
- https://jenkins.io/security/advisory/2019-10-23/#SECURITY-1621
- http://www.openwall.com/lists/oss-security/2019/10/23/2
