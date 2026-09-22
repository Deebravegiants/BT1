# [M] Inclusion of Sensitive Information in Source Code in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-9596
Aliases: CVE-2024-9596
Ecosystem: Bitnami
Published: 2024-10-13
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-9596
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.4.0 <17.4.2

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 16.6 prior to 17.2.9, from 17.3 prior to 17.3.5, and from 17.4 prior to 17.4.2. It was possible for an unauthenticated attacker to determine the GitLab version number for a GitLab instance.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/493355
- https://nvd.nist.gov/vuln/detail/CVE-2024-9596
