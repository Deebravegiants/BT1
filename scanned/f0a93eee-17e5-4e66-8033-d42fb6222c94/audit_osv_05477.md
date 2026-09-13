# [H] Files or Directories Accessible to External Parties in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2025-1042
Aliases: CVE-2025-1042
Ecosystem: Bitnami
Published: 2025-02-17
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-1042
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.7.0 <17.8.2

## Details
An insecure direct object reference vulnerability in GitLab EE affecting all versions from 15.7 prior to 17.6.5, 17.7 prior to 17.7.4, and 17.8 prior to 17.8.2 allows an attacker to view repositories in an unauthorized way.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/50849943
- https://hackerone.com/reports/2886976
- https://nvd.nist.gov/vuln/detail/CVE-2025-1042
