# [M] CVE-2020-2125

## Summary
Severity: Medium
Advisory: CVE-2020-2125
Aliases: GHSA-64jr-ggw8-h9jc
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-02-12
Source: https://osv.dev/vulnerability/CVE-2020-2125
Type: osv

## Details
Jenkins Debian Package Builder Plugin 1.6.11 and earlier stores a GPG passphrase unencrypted in its global configuration file on the Jenkins master where it can be viewed by users with access to the master file system.

## References
- http://www.openwall.com/lists/oss-security/2020/02/12/3
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-1558
