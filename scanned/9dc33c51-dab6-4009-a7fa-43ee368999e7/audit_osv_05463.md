# [H] External Control of Critical State Data in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2024-8754
Aliases: CVE-2024-8754
Ecosystem: Bitnami
Published: 2024-09-14
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-8754
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.3.0 <17.3.2

## Details
An issue has been discovered in GitLab EE/CE affecting all versions from 16.9.7 prior to 17.1.7, 17.2 prior to 17.2.5, and 17.3 prior to 17.3.2. An improper input validation error allows attacker to squat on accounts via linking arbitrary unclaimed provider identities when JWT authentication is configured.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/464062
- https://nvd.nist.gov/vuln/detail/CVE-2024-8754
