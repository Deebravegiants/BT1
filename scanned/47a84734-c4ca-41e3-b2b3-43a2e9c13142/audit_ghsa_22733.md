# [C] Improper Authentication in Jenkins Active Directory Plugin

## Summary
Severity: Critical
Advisory: GHSA-rf92-3vjr-w628
CVE: CVE-2020-2299
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rf92-3vjr-w628
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:active-directory` — affected >=2.17 <2.20
- Maven: `org.jenkins-ci.plugins:active-directory` — affected >=1.44 <2.16.1

## Details
Jenkins Active Directory Plugin implements two separate modes: Integration with ADSI on Windows, and an OS agnostic LDAP-based mode.

The LDAP-based mode in Active Directory Plugin starting in version 1.44 and prior to versions 2.16.1 and 2.20 shares code between user lookup and user authentication and distinguishes these behaviors through the use if a magic constant used in place of a real password. This allows attackers to log in as any user if the magic constant is used as the password in Active Directory Plugin prior to 2.16.1 and 220.

Active Directory Plugin 2.16.1 and 2.20 no longer uses a magic constant to distinguish between user lookup and user authentication.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2299
- https://github.com/jenkinsci/active-directory-plugin/commit/57e78ea7bb96b4e59405f28959ade2d26821163d
- https://github.com/CVEProject/cvelist/blob/16860a328d970faa6e4350b0fa446f64a52e52ca/2020/2xxx/CVE-2020-2299.json
- https://github.com/jenkinsci/active-directory-plugin
- https://www.jenkins.io/security/advisory/2020-11-04/#SECURITY-2117
- http://www.openwall.com/lists/oss-security/2020/11/04/6
