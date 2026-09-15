# [H] CVE-2019-10318

## Summary
Severity: High
Advisory: CVE-2019-10318
Aliases: GHSA-jcwj-j574-8j2c
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-30
Source: https://osv.dev/vulnerability/CVE-2019-10318
Type: osv

## Details
Jenkins Azure AD Plugin 0.3.3 and earlier stored the client secret unencrypted in the global config.xml configuration file on the Jenkins master where it could be viewed by users with access to the master file system.

## References
- http://www.openwall.com/lists/oss-security/2019/04/30/5
- http://www.securityfocus.com/bid/108159
- https://jenkins.io/security/advisory/2019-04-30/#SECURITY-1390
