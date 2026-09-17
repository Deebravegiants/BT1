# [H] User Interface (UI) Misrepresentation of Critical Information in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2024-9163
Aliases: CVE-2024-9163
Ecosystem: Bitnami
Published: 2025-05-28
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-9163
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.0.0 <18.0.1

## Details
A business logic error in GitLab CE/EE affecting all versions starting from 12.1 prior to 17.10.7, 17.11 prior to 17.11.3 and 18.0 prior to 18.0.1 where an attacker can cause a branch name confusion in confidential MRs.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/493942
- https://hackerone.com/reports/2705566
- https://nvd.nist.gov/vuln/detail/CVE-2024-9163
