# [M] Jenkins VMware vRealize Automation Plugin Missing Encryption of Sensitive Data

## Summary
Severity: Medium
Advisory: GHSA-7h99-vjmf-5pg8
CVE: CVE-2019-1003068
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-7h99-vjmf-5pg8
Type: github-advisory

## Affected
- Maven: `com.inkysea.vmware.vra:vmware-vrealize-automation-plugin` — affected >=0

## Details
Jenkins VMware vRealize Automation Plugin stores credentials unencrypted in job `config.xml` files on the Jenkins controller. These credentials can be viewed by users with Extended Read permission, or access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003068
- https://github.com/jenkinsci/vmware-vrealize-automation-plugin
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-945
- https://web.archive.org/web/20200227082017/http://www.securityfocus.com/bid/107790
- http://www.openwall.com/lists/oss-security/2019/04/12/2
