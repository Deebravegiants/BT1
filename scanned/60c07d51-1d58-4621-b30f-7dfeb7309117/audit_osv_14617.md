# [H] CVE-2019-10316

## Summary
Severity: High
Advisory: CVE-2019-10316
Aliases: GHSA-gg8r-24qm-qfch
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-30
Source: https://osv.dev/vulnerability/CVE-2019-10316
Type: osv

## Details
Jenkins Aqua MicroScanner Plugin 1.0.5 and earlier stored credentials unencrypted in its global configuration file on the Jenkins master where they could be viewed by users with access to the master file system.

## References
- http://www.openwall.com/lists/oss-security/2019/04/30/5
- http://www.securityfocus.com/bid/108159
- https://jenkins.io/security/advisory/2019-04-30/#SECURITY-1380
