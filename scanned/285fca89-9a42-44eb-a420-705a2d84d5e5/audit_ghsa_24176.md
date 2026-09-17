# [M] Missing permission checks in Jenkins Fortify on Demand Plugin

## Summary
Severity: Medium
Advisory: GHSA-fhmf-xf2q-4m8p
CVE: CVE-2020-2204
CWE: CWE-285, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fhmf-xf2q-4m8p
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:fortify-on-demand-uploader` — affected >=0 <6.0.1

## Details
A missing permission check in Jenkins Fortify on Demand Plugin 5.0.1 and earlier allows attackers with Overall/Read permission to connect to the globally configured Fortify on Demand endpoint using attacker-specified credentials IDs.

This form validation method requires appropriate permission in Fortify on Demand Plugin 6.0.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2204
- https://github.com/jenkinsci/fortify-on-demand-uploader-plugin/commit/006c2336d578010be707ac029fe6b8cb3497bbc9
- https://github.com/jenkinsci/fortify-on-demand-uploader-plugin/commit/28932f7c5ff18f87d4b3a480225fb0827591776b
- https://github.com/jenkinsci/fortify-on-demand-uploader-plugin
- https://jenkins.io/security/advisory/2020-07-02/#SECURITY-1691
- http://www.openwall.com/lists/oss-security/2020/07/02/7
