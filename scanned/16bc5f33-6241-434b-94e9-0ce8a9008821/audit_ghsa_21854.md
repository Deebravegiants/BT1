# [M] Missing permission check in Jenkins autonomiq Plugin

## Summary
Severity: Medium
Advisory: GHSA-6jv7-28mv-qp9c
CVE: CVE-2022-25195
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-6jv7-28mv-qp9c
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:autonomiq` — affected >=0 <1.16

## Details
A missing permission check in Jenkins autonomiq Plugin 1.15 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25195
- https://github.com/jenkinsci/autonomiq-plugin/commit/e06b1ff67664a90819c9561bbc12f4c6e593d1dc
- https://github.com/jenkinsci/autonomiq-plugin
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2545
