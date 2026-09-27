# [H] BIT-jenkins-2026-84650

## Summary
Severity: High
Advisory: BIT-jenkins-2026-84650
Aliases: CVE-2026-84650
Ecosystem: Bitnami
Published: 2026-09-08
Source: https://osv.dev/vulnerability/BIT-jenkins-2026-84650
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=2.569.0 <2.580.0

## Details
In Jenkins 2.579 and earlier, LTS 2.568.2 and earlier, transient fields cannot be excluded from deserialization, allowing attackers able to submit configuration updates to specify the values of transient fields that will be deserialized, the impact depending on how those fields are used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-84650
- https://www.jenkins.io/security/advisory/2026-09-02/#SECURITY-4032
