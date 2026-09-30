# [M] BIT-jenkins-2023-27904

## Summary
Severity: Medium
Advisory: BIT-jenkins-2023-27904
Aliases: CVE-2023-27904, GHSA-rrgp-c2w8-6vg6
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-jenkins-2023-27904
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=0 <2.394.0

## Details
Jenkins LTS 2.375.3 and earlier prints an error stack trace on agent-related pages when agent connections are broken, potentially revealing information about Jenkins configuration that is otherwise inaccessible to attackers.

## References
- https://www.jenkins.io/security/advisory/2023-03-08/#SECURITY-2120
- https://nvd.nist.gov/vuln/detail/CVE-2023-27904
