# [M] Missing permission checks in Google Kubernetes Engine Jenkins Plugin

## Summary
Severity: Medium
Advisory: GHSA-wwr4-79jv-297r
CVE: CVE-2019-10445
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-wwr4-79jv-297r
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:google-kubernetes-engine` — affected >=0 <0.7.1

## Details
A missing permission check in Jenkins Google Kubernetes Engine Plugin Prior to version 0.7.1 allows attackers with Overall/Read permission to obtain limited information about the scope of a credential with an attacker-specified credentials ID. This issue is patched in version 0.7.1

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10445
- https://github.com/jenkinsci/google-kubernetes-engine-plugin
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1607
- http://www.openwall.com/lists/oss-security/2019/10/16/6
