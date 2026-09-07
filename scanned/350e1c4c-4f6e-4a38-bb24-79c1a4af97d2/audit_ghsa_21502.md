# [M] Plaintext Storage of a Password in Jenkins NS-ND Integration Performance Publisher Plugin

## Summary
Severity: Medium
Advisory: GHSA-x2w2-5552-fjv6
CVE: CVE-2022-45392
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-x2w2-5552-fjv6
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:cavisson-ns-nd-integration` — affected >=0 <4.8.0.146

## Details
NS-ND Integration Performance Publisher Plugin 4.8.0.143 and earlier stores passwords unencrypted in job `config.xml` files on the Jenkins controller as part of its configuration.

These passwords can be viewed by attackers with Item/Extended Read permission or access to the Jenkins controller file system.

NS-ND Integration Performance Publisher Plugin 4.8.0.146 stores passwords encrypted once job configurations are saved again.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45392
- https://github.com/jenkinsci/cavisson-ns-nd-integration-plugin
- https://www.jenkins.io/security/advisory/2022-11-15/#SECURITY-2912
- http://www.openwall.com/lists/oss-security/2022/11/15/4
