# [H] OS command injection in CryptoMove Plugin

## Summary
Severity: High
Advisory: GHSA-p5x5-jg3j-2jcj
CVE: CVE-2020-2159
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p5x5-jg3j-2jcj
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:cryptomove` — affected >=0

## Details
CryptoMove Plugin 0.1.33 and earlier allows the configuration of an OS command to execute as part of its build step configuration. This command will be executed on the Jenkins controller as the OS user account running Jenkins, allowing user with Job/Configure permission to execute an arbitrary OS command on the Jenkins controller.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2159
- https://github.com/jenkinsci/cryptomove-plugin
- https://jenkins.io/security/advisory/2020-03-09/#SECURITY-1635
- http://www.openwall.com/lists/oss-security/2020/03/09/1
