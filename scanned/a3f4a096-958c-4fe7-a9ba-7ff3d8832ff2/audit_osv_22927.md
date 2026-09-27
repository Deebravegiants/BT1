# [M] CVE-2022-41255

## Summary
Severity: Medium
Advisory: CVE-2022-41255
Aliases: GHSA-fmq9-r4p2-8272
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-09-21
Source: https://osv.dev/vulnerability/CVE-2022-41255
Type: osv

## Details
Jenkins CONS3RT Plugin 1.0.0 and earlier stores Cons3rt API token unencrypted in job config.xml files on the Jenkins controller where it can be viewed by users with access to the Jenkins controller file system.

## References
- http://www.openwall.com/lists/oss-security/2022/09/21/5
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2759
