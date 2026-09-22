# [M] Jenkins Libvirt Slaves Plugin vlnerable to Incorrect Default Permissions

## Summary
Severity: Medium
Advisory: GHSA-m36j-f2hf-qgj2
CVE: CVE-2019-10472
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m36j-f2hf-qgj2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:libvirt-slave` — affected >=0 <1.8.6

## Details
A missing permission check in Jenkins Libvirt Slaves Plugin allows attackers with Overall/Read permission to connect to an attacker-specified SSH server using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10472
- https://github.com/jenkinsci/libvirt-slave-plugin/commit/231c41e0e4ecb2d25247cc2775e1fe18d64a1703
- https://github.com/jenkinsci/libvirt-slave-plugin/commit/c671d68f9498414a735913c9372ede8b4791bfee
- https://github.com/jenkinsci/libvirt-slave-plugin
- https://jenkins.io/security/advisory/2019-10-23/#SECURITY-1014%20(1)
- http://www.openwall.com/lists/oss-security/2019/10/23/2
