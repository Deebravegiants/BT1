# [M] CVE-2019-10312

## Summary
Severity: Medium
Advisory: CVE-2019-10312
Aliases: GHSA-7mvg-cx9c-r6jm
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-04-30
Source: https://osv.dev/vulnerability/CVE-2019-10312
Type: osv

## Details
A missing permission check in Jenkins Ansible Tower Plugin 0.9.1 and earlier in the TowerInstallation.TowerInstallationDescriptor#doFillTowerCredentialsIdItems method allowed attackers with Overall/Read permission to enumerate credentials ID of credentials stored in Jenkins.

## References
- http://www.openwall.com/lists/oss-security/2019/04/30/5
- http://www.securityfocus.com/bid/108159
- https://jenkins.io/security/advisory/2019-04-30/#SECURITY-1355
