# [M] Missing permission checks in Jenkins Chaos Monkey Plugin

## Summary
Severity: Medium
Advisory: GHSA-hx53-635r-vmv8
CVE: CVE-2020-2323
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hx53-635r-vmv8
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:chaos-monkey` — affected >=0 <0.4.1

## Details
Jenkins Chaos Monkey Plugin 0.4 and earlier does not perform permission checks in an HTTP endpoint.

This allows attackers with Overall/Read permission to access the Chaos Monkey page and to see the history of actions.

Jenkins Chaos Monkey Plugin 0.4.1 requires Overall/Administer permission to access the Chaos Monkey page and to see the history of actions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2323
- https://github.com/jenkinsci/chaos-monkey-plugin
- https://www.jenkins.io/security/advisory/2020-12-03/#SECURITY-2109%20(2)
- http://www.openwall.com/lists/oss-security/2020/12/03/2
