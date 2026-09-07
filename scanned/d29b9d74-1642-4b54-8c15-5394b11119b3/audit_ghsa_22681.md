# [M] Jenkins vSphere Plugin disables SSL/TLS certificate validation by default

## Summary
Severity: Medium
Advisory: GHSA-vq7p-f4fv-rr5x
CVE: CVE-2018-1000151
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-vq7p-f4fv-rr5x
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:vsphere-cloud` — affected >=0 <2.17

## Details
A man in the middle vulnerability exists in Jenkins vSphere Plugin 2.16 and older in VSphere.java that disables SSL/TLS certificate validation by default. vSphere Plugin 2.17 now has SSL/TLS certificate validation enabled by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000151
- https://github.com/jenkinsci/vsphere-cloud-plugin/commit/f0fb143af340c7529dd9e50f5514334756019356
- https://github.com/jenkinsci/vsphere-cloud-plugin
- https://jenkins.io/security/advisory/2018-03-26/#SECURITY-504
