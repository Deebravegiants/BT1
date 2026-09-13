# [M] Lack of SSL/TLS certificate and hostname validation in Amazon EC2 Plugin

## Summary
Severity: Medium
Advisory: GHSA-c89c-pvm7-33wj
CVE: CVE-2020-2187
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c89c-pvm7-33wj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ec2` — affected >=0 <1.50.2

## Details
Amazon EC2 Plugin connects to Windows agents via HTTPS.

Amazon EC2 Plugin 1.50.1 and earlier unconditionally accepts self-signed HTTPS certificates and does not perform hostname validation when connecting to Windows agents. This lack of validation could be abused using a man-in-the-middle attack to intercept these connections to build agents.

Amazon EC2 Plugin 1.50.2 by default no longer accepts self-signed HTTPS certificates and performs hostname validation. A new configuration option allows restoring the previous, unsafe behavior. For more information see [the plugin documentation](https://github.com/jenkinsci/ec2-plugin/#securing-the-connection-to-windows-amis).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2187
- https://github.com/jenkinsci/ec2-plugin/commit/4c9f03ae202e4730fd54eda40771fa4d3873e358
- https://github.com/jenkinsci/ec2-plugin
- https://jenkins.io/security/advisory/2020-05-06/#SECURITY-1528
- http://www.openwall.com/lists/oss-security/2020/05/06/3
