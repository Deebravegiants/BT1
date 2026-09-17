# [H] Unintended Proxy or Intermediary ('Confused Deputy') in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2024-9870
Aliases: CVE-2024-9870
Ecosystem: Bitnami
Published: 2025-02-17
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-9870
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.11.0 <17.8.2

## Details
An external service interaction vulnerability in GitLab EE affecting all versions from 15.11 prior to 17.6.5, 17.7 prior to 17.7.4, and 17.8 prior to 17.8.2 allows an attacker to send requests from the GitLab server to unintended services.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/498911
- https://hackerone.com/reports/2734142
- https://nvd.nist.gov/vuln/detail/CVE-2024-9870
