# [M] CVE-2019-1003081

## Summary
Severity: Medium
Advisory: CVE-2019-1003081
Aliases: GHSA-m46p-rp8x-x8c4
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-04-04
Source: https://osv.dev/vulnerability/CVE-2019-1003081
Type: osv

## Details
A missing permission check in Jenkins OpenShift Deployer Plugin in the DeployApplication.DeployApplicationDescriptor#doCheckLogin form validation method allows attackers with Overall/Read permission to initiate a connection to an attacker-specified server.

## References
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-981
