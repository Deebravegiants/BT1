# [M] CVE-2019-10415

## Summary
Severity: Medium
Advisory: CVE-2019-10415
Aliases: GHSA-8hwr-589g-xpj2
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-09-25
Source: https://osv.dev/vulnerability/CVE-2019-10415
Type: osv

## Details
Jenkins Violation Comments to GitLab Plugin 2.28 and earlier stored credentials unencrypted in its global configuration file on the Jenkins master where they could be viewed by users with access to the master file system.

## References
- http://www.openwall.com/lists/oss-security/2019/09/25/3
- https://jenkins.io/security/advisory/2019-09-25/#SECURITY-1577
