# [M] Jenkins Active Directory Plugin vulnerable to Active Directory credential disclosure

## Summary
Severity: Medium
Advisory: GHSA-g8c3-6fj2-87w7
CVE: CVE-2023-37943
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-g8c3-6fj2-87w7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:active-directory` — affected >=0 <2.30.1

## Details
Jenkins Active Directory Plugin allows testing a new, unsaved configuration by performing a connection test (the button labeled "Test Domain").

Active Directory Plugin 2.30 and earlier ignores the "Require TLS" and "StartTls" options and always performs the connection test to Active directory unencrypted. This allows attackers able to capture network traffic between the Jenkins controller and Active Directory servers to obtain Active Directory credentials.

This only affects the connection test. Connections established during the login process are encrypted if the corresponding TLS option is enabled.

Active Directory Plugin 2.30.1 considers the "Require TLS" and "StartTls" options for connection tests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37943
- https://github.com/jenkinsci/active-directory-plugin/commit/549dde617dbcf533e6cabfe8cc148a250a398211
- https://www.jenkins.io/security/advisory/2023-07-12/#SECURITY-3059
- http://www.openwall.com/lists/oss-security/2023/07/12/2
