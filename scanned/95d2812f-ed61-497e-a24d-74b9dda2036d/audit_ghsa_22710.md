# [H] Jenkins Active Directory Plugin Improper certificate validation with StartTLS

## Summary
Severity: High
Advisory: GHSA-2h95-4xw9-m68j
CVE: CVE-2019-1003009
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-2h95-4xw9-m68j
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:active-directory` — affected >=0 <2.11

## Details
An improper certificate validation vulnerability exists in Jenkins Active Directory Plugin 2.10 and earlier in src/main/java/hudson/plugins/active_directory/ActiveDirectoryDomain.java, src/main/java/hudson/plugins/active_directory/ActiveDirectorySecurityRealm.java, src/main/java/hudson/plugins/active_directory/ActiveDirectoryUnixAuthenticationProvider.java that allows attackers to impersonate the Active Directory server Jenkins connects to for authentication if Jenkins is configured to use StartTLS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003009
- https://github.com/jenkinsci/active-directory-plugin/commit/520faf5bb1078d75e5fed10b7bf5ac6241fe2fc4
- https://github.com/jenkinsci/active-directory-plugin
- https://jenkins.io/security/advisory/2019-01-28/#SECURITY-859
