# [M] Privilege Context Switching Error in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-12570
Aliases: CVE-2024-12570
Ecosystem: Bitnami
Published: 2024-12-16
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-12570
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.6.0 <17.6.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 13.7 prior to 17.4.6, from 17.5 prior to 17.5.4, and from 17.6 prior to 17.6.2. It may have been possible for an attacker with a victim's `CI_JOB_TOKEN` to obtain a GitLab session token belonging to the victim.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/494694
- https://hackerone.com/reports/2724948
- https://nvd.nist.gov/vuln/detail/CVE-2024-12570
