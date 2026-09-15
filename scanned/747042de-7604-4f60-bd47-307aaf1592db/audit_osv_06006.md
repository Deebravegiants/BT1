# [H] BIT-jenkins-2023-43497

## Summary
Severity: High
Advisory: BIT-jenkins-2023-43497
Aliases: CVE-2023-43497, GHSA-qv64-w99c-qcr9
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-jenkins-2023-43497
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=0 <2.424.0

## Details
In Jenkins LTS 2.414.1 and earlier, processing file uploads using the Stapler web framework creates temporary files in the default system temporary directory with the default permissions for newly created files, potentially allowing attackers with access to the Jenkins controller file system to read and write the files before they are used.

## References
- http://www.openwall.com/lists/oss-security/2023/09/20/5
- https://www.jenkins.io/security/advisory/2023-09-20/#SECURITY-3073
- https://nvd.nist.gov/vuln/detail/CVE-2023-43497
