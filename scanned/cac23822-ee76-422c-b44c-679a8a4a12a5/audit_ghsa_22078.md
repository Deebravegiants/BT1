# [H] Jenkins Libvirt Slaves Plugin vlnerable to Cross-Site Request Forgery

## Summary
Severity: High
Advisory: GHSA-m295-m3x4-3mmc
CVE: CVE-2019-10471
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m295-m3x4-3mmc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:libvirt-slave` — affected >=0 <1.8.6

## Details
A cross-site request forgery vulnerability in Jenkins Libvirt Slaves Plugin allows attackers to connect to an attacker-specified SSH server using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10471
- https://github.com/jenkinsci/libvirt-slave-plugin/commit/231c41e0e4ecb2d25247cc2775e1fe18d64a1703
- https://github.com/jenkinsci/libvirt-slave-plugin
- https://jenkins.io/security/advisory/2019-10-23/#SECURITY-1014%20(1)
- http://www.openwall.com/lists/oss-security/2019/10/23/2
