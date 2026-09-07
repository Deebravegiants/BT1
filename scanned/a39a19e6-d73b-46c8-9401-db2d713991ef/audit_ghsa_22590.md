# [M] CSRF vulnerability in Jenkins Nomad Plugin allow SSRF

## Summary
Severity: Medium
Advisory: GHSA-fvcf-wgxj-h7ch
CVE: CVE-2019-10292
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-fvcf-wgxj-h7ch
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:kmap-jenkins` — affected 1.6

## Details
A cross-site request forgery vulnerability in Jenkins Kmap Plugin in KmapJenkinsBuilder.DescriptorImpl form validation methods allows attackers to initiate a connection to an attacker-specified server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10292
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-1055
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
