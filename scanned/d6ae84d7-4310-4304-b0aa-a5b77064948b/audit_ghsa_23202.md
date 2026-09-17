# [M] Jenkins Google Cloud Messaging Notification Plugin stores credentials in plain text 

## Summary
Severity: Medium
Advisory: GHSA-c3r5-vxj6-62mc
CVE: CVE-2019-10379
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c3r5-vxj6-62mc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:gcm-notification` — affected >=0

## Details
Jenkins Google Cloud Messaging Notification Plugin 1.0 and earlier stores credentials unencrypted in its global configuration file on the Jenkins master where they can be viewed by users with access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10379
- https://jenkins.io/security/advisory/2019-08-07/#SECURITY-591
- http://www.openwall.com/lists/oss-security/2019/08/07/1
