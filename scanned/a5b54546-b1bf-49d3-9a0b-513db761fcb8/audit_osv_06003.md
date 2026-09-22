# [H] BIT-jenkins-2023-27900

## Summary
Severity: High
Advisory: BIT-jenkins-2023-27900
Aliases: CVE-2023-27900, GHSA-frgr-c5f2-8qhh
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-jenkins-2023-27900
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=0 <2.394.0

## Details
Jenkins LTS 2.375.3 and earlier uses the Apache Commons FileUpload library without specifying limits for the number of request parts introduced in version 1.5 for CVE-2023-24998 in hudson.util.MultipartFormDataParser, allowing attackers to trigger a denial of service.

## References
- https://www.jenkins.io/security/advisory/2023-03-08/#SECURITY-3030
- https://nvd.nist.gov/vuln/detail/CVE-2023-27900
