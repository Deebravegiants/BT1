# [M] CVE-2022-27206

## Summary
Severity: Medium
Advisory: CVE-2022-27206
Aliases: GHSA-hx3r-qwxv-5jw9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-03-15
Source: https://osv.dev/vulnerability/CVE-2022-27206
Type: osv

## Details
Jenkins GitLab Authentication Plugin 1.13 and earlier stores the GitLab client secret unencrypted in the global config.xml file on the Jenkins controller where it can be viewed by users with access to the Jenkins controller file system.

## References
- http://www.openwall.com/lists/oss-security/2022/03/15/2
- https://www.jenkins.io/security/advisory/2022-03-15/#SECURITY-1891
