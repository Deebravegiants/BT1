# [M] Plaintext storage in Jenkins instant-messaging Plugin

## Summary
Severity: Medium
Advisory: GHSA-hpm9-fx8v-w45v
CVE: CVE-2022-28135
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-hpm9-fx8v-w45v
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:instant-messaging` — affected >=0 <1.42

## Details
Jenkins instant-messaging Plugin 1.41 and earlier stores passwords for group chats unencrypted in the global configuration file of plugins based on Jenkins instant-messaging Plugin on the Jenkins controller where they can be viewed by users with access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28135
- https://github.com/jenkinsci/instant-messaging-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-2161
- http://www.openwall.com/lists/oss-security/2022/03/29/1
