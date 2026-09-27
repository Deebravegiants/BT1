# [H] BIT-jenkins-2023-43498

## Summary
Severity: High
Advisory: BIT-jenkins-2023-43498
Aliases: CVE-2023-43498, GHSA-hq87-h4jg-vxfw
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-jenkins-2023-43498
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=0 <2.424.0

## Details
In Jenkins LTS 2.414.1 and earlier, processing file uploads using MultipartFormDataParser creates temporary files in the default system temporary directory with the default permissions for newly created files, potentially allowing attackers with access to the Jenkins controller file system to read and write the files before they are used.

## References
- http://www.openwall.com/lists/oss-security/2023/09/20/5
- https://www.jenkins.io/security/advisory/2023-09-20/#SECURITY-3073
- https://nvd.nist.gov/vuln/detail/CVE-2023-43498
