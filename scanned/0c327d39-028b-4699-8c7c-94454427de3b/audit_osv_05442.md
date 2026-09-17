# [M] Improper Restriction of Rendered UI Layers or Frames in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-2177
Aliases: CVE-2024-2177
Ecosystem: Bitnami
Published: 2024-07-11
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-2177
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.1.0 <17.1.1

## Details
A Cross Window Forgery vulnerability exists within GitLab CE/EE affecting all versions from 16.3 prior to 16.11.5, 17.0 prior to 17.0.3, and 17.1 prior to 17.1.1. This condition allows for an attacker to abuse the OAuth authentication flow via a crafted payload.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/444467
- https://hackerone.com/reports/2383443
- https://nvd.nist.gov/vuln/detail/CVE-2024-2177
