# [M] BIT-jenkins-2025-27623

## Summary
Severity: Medium
Advisory: BIT-jenkins-2025-27623
Aliases: CVE-2025-27623, GHSA-rfh6-9r2q-98vf
Ecosystem: Bitnami
Published: 2025-03-07
Source: https://osv.dev/vulnerability/BIT-jenkins-2025-27623
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=2.493.0 <2.504.1

## Details
Jenkins 2.499 and earlier, LTS 2.492.1 and earlier does not redact encrypted values of secrets when accessing `config.xml` of views via REST API or CLI, allowing attackers with View/Read permission to view encrypted values of secrets.

## References
- https://www.jenkins.io/security/advisory/2025-03-05/#SECURITY-3496
- https://nvd.nist.gov/vuln/detail/CVE-2025-27623
