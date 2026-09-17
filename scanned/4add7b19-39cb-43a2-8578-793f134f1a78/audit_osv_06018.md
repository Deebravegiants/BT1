# [M] BIT-jenkins-2026-84646

## Summary
Severity: Medium
Advisory: BIT-jenkins-2026-84646
Aliases: CVE-2026-84646
Ecosystem: Bitnami
Published: 2026-09-08
Source: https://osv.dev/vulnerability/BIT-jenkins-2026-84646
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=2.569.0 <2.580.0

## Details
In Jenkins 2.579 and earlier, LTS 2.568.2 and earlier, user objects can appear as nested field values in other deserialized XML objects, allowing attackers with Overall/Read permission to create user objects by submitting crafted XML.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-84646
- https://www.jenkins.io/security/advisory/2026-09-02/#SECURITY-3908
