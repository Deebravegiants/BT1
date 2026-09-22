# [C] BIT-jenkins-2021-21692

## Summary
Severity: Critical
Advisory: BIT-jenkins-2021-21692
Aliases: CVE-2021-21692, GHSA-8xg4-xq2v-v6j7
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-jenkins-2021-21692
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=0 <2.319.0

## Details
FilePath#renameTo and FilePath#moveAllChildrenTo in Jenkins LTS 2.303.2 and earlier only check 'read' agent-to-controller access permission on the source path, instead of 'delete'.

## References
- https://www.jenkins.io/security/advisory/2021-11-04/#SECURITY-2455
- https://nvd.nist.gov/vuln/detail/CVE-2021-21692
