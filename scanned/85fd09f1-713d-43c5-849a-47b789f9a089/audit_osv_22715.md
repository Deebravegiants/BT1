# [M] CVE-2022-36901

## Summary
Severity: Medium
Advisory: CVE-2022-36901
Aliases: GHSA-2qh6-hhvv-m2ww
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-07-27
Source: https://osv.dev/vulnerability/CVE-2022-36901
Type: osv

## Details
Jenkins HTTP Request Plugin 1.15 and earlier stores HTTP Request passwords unencrypted in its global configuration file on the Jenkins controller where they can be viewed by users with access to the Jenkins controller file system.

## References
- http://www.openwall.com/lists/oss-security/2022/07/27/1
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2053
