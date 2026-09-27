# [C] BIT-jenkins-2021-21691

## Summary
Severity: Critical
Advisory: BIT-jenkins-2021-21691
Aliases: CVE-2021-21691, GHSA-2c79-h2h5-g3fw
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-jenkins-2021-21691
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=0 <2.319.0

## Details
Creating symbolic links is possible without the 'symlink' agent-to-controller access control permission in Jenkins LTS 2.303.2 and earlier.

## References
- https://www.jenkins.io/security/advisory/2021-11-04/#SECURITY-2455
- https://nvd.nist.gov/vuln/detail/CVE-2021-21691
