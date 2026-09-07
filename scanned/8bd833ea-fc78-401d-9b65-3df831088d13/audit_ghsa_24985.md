# [M] CSRF vulnerability in Mac Plugin

## Summary
Severity: Medium
Advisory: GHSA-qcfq-35v7-4fw7
CVE: CVE-2020-2147
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qcfq-35v7-4fw7
Type: github-advisory

## Affected
- Maven: `fr.edf.jenkins.plugins:mac` — affected >=0 <1.2.0

## Details
A cross-site request forgery vulnerability in Jenkins Mac Plugin 1.1.0 and earlier allows attackers to connect to an attacker-specified SSH server using attacker-specified credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2147
- https://github.com/jenkinsci/mac-plugin/commit/86aebd3d33526d83d6cbc9aef7fb1f4831fb1805
- https://github.com/jenkinsci/mac-plugin
- https://jenkins.io/security/advisory/2020-03-09/#SECURITY-1761
- http://www.openwall.com/lists/oss-security/2020/03/09/1
