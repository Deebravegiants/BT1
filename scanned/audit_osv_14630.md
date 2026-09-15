# [H] CVE-2019-10348

## Summary
Severity: High
Advisory: CVE-2019-10348
Aliases: GHSA-q736-rgcp-q443
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-11
Source: https://osv.dev/vulnerability/CVE-2019-10348
Type: osv

## Details
Jenkins Gogs Plugin stored credentials unencrypted in job config.xml files on the Jenkins master where they can be viewed by users with Extended Read permission, or access to the master file system.

## References
- http://www.openwall.com/lists/oss-security/2019/07/11/4
- http://www.securityfocus.com/bid/109156
- https://jenkins.io/security/advisory/2019-07-11/#SECURITY-1438
- https://www.zerodayinitiative.com/advisories/ZDI-19-837/
