# [M] Jenkins Dependency Graph Viewer plugin vulnerable to missing permission checks

## Summary
Severity: Medium
Advisory: GHSA-vhh3-mvc4-hhq6
CVE: CVE-2017-1000388
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vhh3-mvc4-hhq6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:depgraph-view` — affected >=0 <0.13

## Details
Jenkins Dependency Graph Viewer plugin 0.12 and earlier did not perform permission checks for the API endpoint that modifies the dependency graph, allowing anyone with Overall/Read permission to modify this data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000388
- https://jenkins.io/security/advisory/2017-10-23
