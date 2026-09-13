# [H] BIT-jenkins-2026-84647

## Summary
Severity: High
Advisory: BIT-jenkins-2026-84647
Aliases: CVE-2026-84647
Ecosystem: Bitnami
Published: 2026-09-08
Source: https://osv.dev/vulnerability/BIT-jenkins-2026-84647
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=2.569.0 <2.580.0

## Details
In Stapler 2107.v8dfcb_e8ed317 and earlier, except 2088.2093.vd7c3e58008a_6, included in Jenkins 2.579 and earlier, LTS 2.568.2 and earlier, Stapler does not restrict the types of objects that can be instantiated via form data binding to those compatible with the expected field type, allowing attackers with Overall/Read permission to instantiate types related to configuration for which that field type was not intended.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-84647
- https://www.jenkins.io/security/advisory/2026-09-02/#SECURITY-3915
