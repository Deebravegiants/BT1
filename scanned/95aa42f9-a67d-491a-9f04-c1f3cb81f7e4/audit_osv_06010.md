# [M] BIT-jenkins-2025-31720

## Summary
Severity: Medium
Advisory: BIT-jenkins-2025-31720
Aliases: CVE-2025-31720, GHSA-565r-pf5q-45v6
Ecosystem: Bitnami
Published: 2025-04-04
Source: https://osv.dev/vulnerability/BIT-jenkins-2025-31720
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=2.493.0 <2.504.1

## Details
A missing permission check in Jenkins 2.503 and earlier, LTS 2.492.2 and earlier allows attackers with Computer/Create permission but without Computer/Extended Read permission to copy an agent, gaining access to its configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-31720
- https://www.jenkins.io/security/advisory/2025-04-02/#SECURITY-3512
