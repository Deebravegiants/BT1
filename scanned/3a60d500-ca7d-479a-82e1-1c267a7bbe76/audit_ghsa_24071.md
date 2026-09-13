# [M] Jenkins Mattermost Notification Plugin contains unencrypted storage of secret token

## Summary
Severity: Medium
Advisory: GHSA-xcj6-4355-2823
CVE: CVE-2019-10459
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xcj6-4355-2823
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:mattermost` — affected >=0 <2.7.1

## Details
Jenkins Mattermost Notification Plugin 2.7.0 and earlier stored webhook URLs containing a secret token unencrypted in its global configuration file and job config.xml files on the Jenkins master where they could be viewed by users with Extended Read permission, or access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10459
- https://github.com/jenkinsci/mattermost-plugin/commit/c6e509307812d93ba295a35dea95016f007de158
- https://github.com/jenkinsci/mattermost-plugin
- https://jenkins.io/security/advisory/2019-10-23/#SECURITY-1628
- http://www.openwall.com/lists/oss-security/2019/10/23/2
