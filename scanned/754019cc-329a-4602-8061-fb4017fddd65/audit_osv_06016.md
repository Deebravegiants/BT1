# [H] BIT-jenkins-2026-70429

## Summary
Severity: High
Advisory: BIT-jenkins-2026-70429
Aliases: CVE-2026-70429
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-jenkins-2026-70429
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=2.569.0 <2.576.0

## Details
Jenkins 2.575 and earlier, LTS 2.568.1 and earlier handles case-insensitivity in user names and group names inconsistently, allowing attackers able to create new users or groups with names that case-insensitively match other characters to impersonate other users or be granted their permissions in some circumstances.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-70429
- https://www.jenkins.io/security/advisory/2026-08-05/#SECURITY-3924
