# [H] BIT-jenkins-2021-21688

## Summary
Severity: High
Advisory: BIT-jenkins-2021-21688
Aliases: CVE-2021-21688, GHSA-m9hr-259f-2v23
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-jenkins-2021-21688
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=0 <2.319.0

## Details
The agent-to-controller security check FilePath#reading(FileVisitor) in Jenkins LTS 2.303.2 and earlier does not reject any operations, allowing users to have unrestricted read access using certain operations (creating archives, FilePath#copyRecursiveTo).

## References
- https://www.jenkins.io/security/advisory/2021-11-04/#SECURITY-2455
- https://nvd.nist.gov/vuln/detail/CVE-2021-21688
