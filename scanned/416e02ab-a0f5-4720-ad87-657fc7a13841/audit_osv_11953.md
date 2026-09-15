# [M] CVE-2018-1000186

## Summary
Severity: Medium
Advisory: CVE-2018-1000186
Aliases: GHSA-92rv-mvmj-47qh
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-06-05
Source: https://osv.dev/vulnerability/CVE-2018-1000186
Type: osv

## Details
A exposure of sensitive information vulnerability exists in Jenkins GitHub Pull Request Builder Plugin 1.41.0 and older in GhprbGitHubAuth.java that allows attackers with Overall/Read access to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://jenkins.io/security/advisory/2018-06-04/#SECURITY-805
