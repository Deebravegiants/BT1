# [M] Jenkins NS-ND Integration Performance Publisher Plugin disables SSL/TLS certificate validation globally and unconditionally

## Summary
Severity: Medium
Advisory: GHSA-3vwm-fc87-mq6h
CVE: CVE-2022-45391
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-3vwm-fc87-mq6h
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:cavisson-ns-nd-integration` — affected >=0 <4.8.0.146

## Details
Jenkins NS-ND Integration Performance Publisher Plugin 4.8.0.143 and earlier globally and unconditionally disables SSL/TLS certificate and hostname validation for the entire Jenkins controller JVM.

NS-ND Integration Performance Publisher Plugin 4.8.0.146 no longer disables SSL/TLS certificate and hostname validation globally.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45391
- https://github.com/jenkinsci/cavisson-ns-nd-integration-plugin
- https://www.jenkins.io/security/advisory/2022-11-15/#SECURITY-2910%20%281%29
- https://www.jenkins.io/security/advisory/2022-11-15/#SECURITY-2910%20(1)
- http://www.openwall.com/lists/oss-security/2022/11/15/4
