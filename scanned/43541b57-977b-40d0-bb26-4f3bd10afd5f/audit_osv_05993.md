# [C] BIT-jenkins-2021-21690

## Summary
Severity: Critical
Advisory: BIT-jenkins-2021-21690
Aliases: CVE-2021-21690, GHSA-97c3-w9cr-6qc2
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-jenkins-2021-21690
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=0 <2.319.0

## Details
Agent processes are able to completely bypass file path filtering by wrapping the file operation in an agent file path in Jenkins LTS 2.303.2 and earlier.

## References
- https://www.jenkins.io/security/advisory/2021-11-04/#SECURITY-2455
- https://nvd.nist.gov/vuln/detail/CVE-2021-21690
