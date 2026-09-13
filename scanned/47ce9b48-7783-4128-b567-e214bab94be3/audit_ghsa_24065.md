# [M] Missing Authorization in Jenkins Kubernetes Plugin

## Summary
Severity: Medium
Advisory: GHSA-rr6j-37cv-c7x7
CVE: CVE-2020-2308
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rr6j-37cv-c7x7
Type: github-advisory

## Affected
- Maven: `org.csanchez.jenkins.plugins:kubernetes` — affected >=1.27.1 <1.27.4
- Maven: `org.csanchez.jenkins.plugins:kubernetes` — affected >=1.26.0 <1.26.5
- Maven: `org.csanchez.jenkins.plugins:kubernetes` — affected >=1.22.0 <1.25.4.1
- Maven: `org.csanchez.jenkins.plugins:kubernetes` — affected >=0 <1.21.6

## Details
Jenkins Kubernetes Plugin prior to 1.27.4, 1.26.5, 1.25.4.1, and 1.21.6 does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to list global pod template names.

Kubernetes Plugin 1.27.4, 1.26.5, 1.25.4.1, and 1.21.6 requires Overall/Administer permission to list global pod template names.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2308
- https://github.com/jenkinsci/kubernetes-plugin/commit/7aac20940e637cdd2e38d3afd3748704e4015782
- https://www.jenkins.io/security/advisory/2020-11-04/#SECURITY-2102
