# [M] CVE-2018-6356

## Summary
Severity: Medium
Advisory: CVE-2018-6356
Aliases: GHSA-5p59-v5wm-77v4
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-02-20
Source: https://osv.dev/vulnerability/CVE-2018-6356
Type: osv

## Details
Jenkins before 2.107 and Jenkins LTS before 2.89.4 did not properly prevent specifying relative paths that escape a base directory for URLs accessing plugin resource files. This allowed users with Overall/Read permission to download files from the Jenkins master they should not have access to. On Windows, any file accessible to the Jenkins master process could be downloaded. On other operating systems, any file within the Jenkins home directory accessible to the Jenkins master process could be downloaded.

## References
- http://www.openwall.com/lists/oss-security/2018/02/14/1
- http://www.securityfocus.com/bid/103037
- https://jenkins.io/security/advisory/2018-02-14/
- https://www.oracle.com/security-alerts/cpuapr2022.html
