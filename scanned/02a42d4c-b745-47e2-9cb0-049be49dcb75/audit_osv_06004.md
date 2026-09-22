# [M] BIT-jenkins-2023-27903

## Summary
Severity: Medium
Advisory: BIT-jenkins-2023-27903
Aliases: CVE-2023-27903, GHSA-584m-7r4m-8j6v
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-jenkins-2023-27903
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=0 <2.394.0

## Details
Jenkins LTS 2.375.3 and earlier creates a temporary file in the default temporary directory with the default permissions for newly created files when uploading a file parameter through the CLI, potentially allowing attackers with access to the Jenkins controller file system to read and write the file before it is used.

## References
- https://www.jenkins.io/security/advisory/2023-03-08/#SECURITY-3058
- https://nvd.nist.gov/vuln/detail/CVE-2023-27903
