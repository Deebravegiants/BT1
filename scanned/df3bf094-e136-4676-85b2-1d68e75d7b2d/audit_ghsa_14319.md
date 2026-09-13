# [M] Jenkins Consul KV Builder Plugin stores HashiCorp Consul ACL Token unencrypted

## Summary
Severity: Medium
Advisory: GHSA-54cw-rvr3-w6cx
CVE: CVE-2023-30531
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-04-12
Source: https://github.com/advisories/GHSA-54cw-rvr3-w6cx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:consul-kv-builder` — affected >=0

## Details
Jenkins Consul KV Builder Plugin 2.0.13 and earlier stores the HashiCorp Consul ACL Token unencrypted in its global configuration file `org.jenkinsci.plugins.consulkv.GlobalConsulConfig.xml` on the Jenkins controller as part of its configuration.

This token can be viewed by users with access to the Jenkins controller file system.

Additionally, the global configuration form does not mask the token, increasing the potential for attackers to observe and capture it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30531
- https://www.jenkins.io/security/advisory/2023-04-12/#SECURITY-2944
- http://www.openwall.com/lists/oss-security/2023/04/13/3
