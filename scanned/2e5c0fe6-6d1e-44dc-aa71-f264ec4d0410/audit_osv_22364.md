# [M] CVE-2022-27195

## Summary
Severity: Medium
Advisory: CVE-2022-27195
Aliases: GHSA-5mpf-hw8f-86w9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-03-15
Source: https://osv.dev/vulnerability/CVE-2022-27195
Type: osv

## Details
Jenkins Parameterized Trigger Plugin 2.43 and earlier captures environment variables passed to builds triggered using Jenkins Parameterized Trigger Plugin, including password parameter values, in their `build.xml` files. These values are stored unencrypted and can be viewed by users with access to the Jenkins controller file system.

## References
- http://www.openwall.com/lists/oss-security/2022/03/15/2
- https://www.jenkins.io/security/advisory/2022-03-15/#SECURITY-2185
