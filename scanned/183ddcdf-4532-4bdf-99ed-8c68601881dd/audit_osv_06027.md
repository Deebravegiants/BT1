# [M] BIT-jenkins-2026-84656

## Summary
Severity: Medium
Advisory: BIT-jenkins-2026-84656
Aliases: CVE-2026-84656
Ecosystem: Bitnami
Published: 2026-09-08
Source: https://osv.dev/vulnerability/BIT-jenkins-2026-84656
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=2.569.0 <2.580.0

## Details
A missing permission check in Jenkins 2.579 and earlier, LTS 2.568.2 and earlier allows attackers with Item/Read permission on at least one job to read build parameter names and values of jobs they have no access to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-84656
- https://www.jenkins.io/security/advisory/2026-09-02/#SECURITY-4006
