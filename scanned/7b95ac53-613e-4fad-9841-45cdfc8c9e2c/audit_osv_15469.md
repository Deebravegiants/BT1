# [M] CVE-2019-16556

## Summary
Severity: Medium
Advisory: CVE-2019-16556
Aliases: GHSA-qh3m-c6hw-5hmv
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-12-17
Source: https://osv.dev/vulnerability/CVE-2019-16556
Type: osv

## Details
Jenkins Rundeck Plugin 3.6.5 and earlier stores credentials unencrypted in its global configuration file and in job config.xml files on the Jenkins master where they can be viewed by users with Extended Read permission, or access to the master file system.

## References
- http://www.openwall.com/lists/oss-security/2019/12/17/1
- https://jenkins.io/security/advisory/2019-12-17/#SECURITY-1636
