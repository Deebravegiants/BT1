# [M] Jenkins Libvirt Slaves Plugin vlnerable to Credential Enumeration

## Summary
Severity: Medium
Advisory: GHSA-8j3m-j6x6-cp5v
CVE: CVE-2019-10473
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8j3m-j6x6-cp5v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:libvirt-slave` — affected >=0 <1.8.6

## Details
A missing permission check in Jenkins Libvirt Slaves Plugin in form-related methods allowed users with Overall/Read access to enumerate credentials ID of credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10473
- https://github.com/jenkinsci/libvirt-slave-plugin/commit/c671d68f9498414a735913c9372ede8b4791bfee
- https://github.com/jenkinsci/libvirt-slave-plugin
- https://github.com/jenkinsci/libvirt-slave-plugin/releases
- https://jenkins.io/security/advisory/2019-10-23/#SECURITY-1014%20(2)
- http://www.openwall.com/lists/oss-security/2019/10/23/2
