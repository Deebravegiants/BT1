# [M] Jenkins Active Directory Plugin follows LDAP referrals by default

## Summary
Severity: Medium
Advisory: GHSA-wrhr-54p6-q97f
CVE: CVE-2026-48918
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-wrhr-54p6-q97f
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:active-directory` — affected >=0 <2.41.1

## Details
Jenkins Active Directory Plugin 2.41 and earlier follows LDAP referrals from the configured Active Directory server by default. These can forward to an RMI URL that causes Jenkins to deserialize attacker-controlled data, resulting in Remote Code Execution (RCE) on the Jenkins controller if deserialization "gadgets" are available on the classpath.

This allows attackers able to control the configured Active Directory server, or able to perform a machine-in-the-middle attack, to execute code on the Jenkins controller.

Active Directory Plugin 2.41.1 no longer follows LDAP referrals by default.

Administrators unable to update to a fixed version can start Jenkins with the Java system property `hudson.plugins.active_directory.referral.ignore` set to `true` to mitigate the vulnerability.

Administrators of Jenkins controllers requiring following LDAP referrals can set the Java system property `hudson.plugins.active_directory.referral.ignore` to `false` to restore the previous behavior.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-48918
- https://github.com/jenkinsci/active-directory-plugin
- https://www.jenkins.io/security/advisory/2026-05-27/#SECURITY-3659
