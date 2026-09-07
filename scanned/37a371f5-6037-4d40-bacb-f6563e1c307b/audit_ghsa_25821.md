# [M] Passwords stored in plain text by Jenkins Vmware vRealize CodeStream Plugin

## Summary
Severity: Medium
Advisory: GHSA-9wvr-x83m-84v4
CVE: CVE-2022-27217
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-03-16
Source: https://github.com/advisories/GHSA-9wvr-x83m-84v4
Type: github-advisory

## Affected
- Maven: `com.vmware.vcac:vmware-vrealize-codestream` — affected >=0

## Details
Jenkins Vmware vRealize CodeStream Plugin 1.2 and earlier stores passwords unencrypted in job config.xml files on the Jenkins controller where they can be viewed by users with Extended Read permission, or access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27217
- https://github.com/jenkinsci/vmware-vrealize-codestream-plugin
- https://www.jenkins.io/security/advisory/2022-03-15/#SECURITY-2238
- http://www.openwall.com/lists/oss-security/2022/03/15/2
