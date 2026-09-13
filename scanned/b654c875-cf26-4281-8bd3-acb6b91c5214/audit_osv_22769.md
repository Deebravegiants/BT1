# [M] CVE-2022-38665

## Summary
Severity: Medium
Advisory: CVE-2022-38665
Aliases: GHSA-qh87-2qvh-5jf8
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-08-23
Source: https://osv.dev/vulnerability/CVE-2022-38665
Type: osv

## Details
Jenkins CollabNet Plugins Plugin 2.0.8 and earlier stores a RabbitMQ password unencrypted in its global configuration file on the Jenkins controller where it can be viewed by users with access to the Jenkins controller file system.

## References
- http://www.openwall.com/lists/oss-security/2022/08/23/2
- https://www.jenkins.io/security/advisory/2022-08-23/#SECURITY-2157
