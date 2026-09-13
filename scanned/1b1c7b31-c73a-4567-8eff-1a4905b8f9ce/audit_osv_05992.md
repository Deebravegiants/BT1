# [C] BIT-jenkins-2021-21689

## Summary
Severity: Critical
Advisory: BIT-jenkins-2021-21689
Aliases: CVE-2021-21689, GHSA-j3cq-h6vh-gx7f
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-jenkins-2021-21689
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=0 <2.319.0

## Details
FilePath#unzip and FilePath#untar were not subject to any agent-to-controller access control in Jenkins LTS 2.303.2 and earlier.

## References
- https://www.jenkins.io/security/advisory/2021-11-04/#SECURITY-2455
- https://nvd.nist.gov/vuln/detail/CVE-2021-21689
