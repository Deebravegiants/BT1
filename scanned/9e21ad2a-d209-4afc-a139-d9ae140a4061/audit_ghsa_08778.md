# [M] Jenkins LDAP Plugin deserializes data from LDAP referrals without validation

## Summary
Severity: Medium
Advisory: GHSA-x9v8-p946-5pwc
CVE: CVE-2026-48917
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-x9v8-p946-5pwc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ldap` — affected >=0 <807.809.vd3a

## Details
Jenkins LDAP Plugin 807.v7d7de30930cf and earlier follows LDAP referrals from the configured LDAP server. These can forward to an RMI URL that causes Jenkins to deserialize attacker-controlled data, resulting in Remote Code Execution (RCE) on the Jenkins controller if deserialization "gadgets" are available on the classpath.

This allows attackers able to control the configured LDAP server, or able to perform a machine-in-the-middle attack, to execute code on the Jenkins controller.

LDAP Plugin 807.809.vd3a_4e5e4ec98 no longer follows LDAP referrals.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-48917
- https://github.com/jenkinsci/ldap-plugin
- https://www.jenkins.io/security/advisory/2026-05-27/#SECURITY-3654
