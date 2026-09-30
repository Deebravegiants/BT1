# [H] Privilege Defined With Unsafe Actions in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2024-8631
Aliases: CVE-2024-8631
Ecosystem: Bitnami
Published: 2024-09-14
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-8631
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.3.0 <17.3.2

## Details
A privilege escalation issue has been discovered in GitLab EE affecting all versions starting from 16.6 prior to 17.1.7, from 17.2 prior to 17.2.5, and from 17.3 prior to 17.3.2. A user assigned the Admin Group Member custom role could have escalated their privileges to include other custom roles.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/462665
- https://hackerone.com/reports/2478469
- https://about.gitlab.com/releases/2024/09/11/patch-release-gitlab-17-3-2-released/
- https://nvd.nist.gov/vuln/detail/CVE-2024-8631
