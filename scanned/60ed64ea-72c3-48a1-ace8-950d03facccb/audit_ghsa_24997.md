# [M] SSRF vulnerability due to missing permission check in Fortify on Demand Uploader Plugin 

## Summary
Severity: Medium
Advisory: GHSA-h3rg-4h5g-8fqg
CVE: CVE-2019-1003047
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-h3rg-4h5g-8fqg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:fortify-on-demand-uploader` — affected >=0 <3.0.11

## Details
A missing permission check in Jenkins Fortify on Demand Uploader Plugin 3.0.10 and earlier allows attackers with Overall/Read permission to initiate a connection to an attacker-specified server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003047
- https://github.com/jenkinsci/fortify-on-demand-uploader-plugin/commit/e555f8d62ef793ce221f471d7172cad847fb9252
- https://github.com/jenkinsci/fortify-on-demand-uploader-plugin
- https://jenkins.io/security/advisory/2019-03-25/#SECURITY-992
- http://www.openwall.com/lists/oss-security/2019/03/28/2
- http://www.securityfocus.com/bid/107628
