# [M] CVE-2019-10319

## Summary
Severity: Medium
Advisory: CVE-2019-10319
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-05-21
Source: https://osv.dev/vulnerability/CVE-2019-10319
Type: osv

## Details
A missing permission check in Jenkins PAM Authentication Plugin 1.5 and earlier, except 1.4.1 in PamSecurityRealm.DescriptorImpl#doTest allowed users with Overall/Read permission to obtain limited information about the file /etc/shadow and the user Jenkins is running as.

## References
- http://www.openwall.com/lists/oss-security/2019/05/21/1
- https://jenkins.io/security/advisory/2019-05-21/#SECURITY-1316
