# [H] Incorrect Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2024-8970
Aliases: CVE-2024-8970
Ecosystem: Bitnami
Published: 2024-10-15
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-8970
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.4.0 <17.4.2

## Details
An issue was discovered in GitLab CE/EE affecting all versions starting from 11.6 prior to 17.2.9, starting from 17.3 prior to 17.3.5, and starting from 17.4 prior to 17.4.2, which allows an attacker to trigger a pipeline as another user under certain circumstances.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/490916
- https://hackerone.com/reports/2724948
- https://nvd.nist.gov/vuln/detail/CVE-2024-8970
