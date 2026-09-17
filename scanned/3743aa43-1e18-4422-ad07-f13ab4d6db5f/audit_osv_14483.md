# [M] CVE-2019-1003096

## Summary
Severity: Medium
Advisory: CVE-2019-1003096
Aliases: GHSA-ffv8-x822-fx73
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-04-04
Source: https://osv.dev/vulnerability/CVE-2019-1003096
Type: osv

## Details
Jenkins TestFairy Plugin stores credentials unencrypted in job config.xml files on the Jenkins master where they can be viewed by users with Extended Read permission, or access to the master file system.

## References
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-1062
