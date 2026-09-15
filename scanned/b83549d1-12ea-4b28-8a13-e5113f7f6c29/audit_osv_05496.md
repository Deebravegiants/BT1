# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-1540
Aliases: CVE-2025-1540
Ecosystem: Bitnami
Published: 2025-03-10
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-1540
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.5.0 <17.8.2

## Details
An issue has been discovered in GitLab CE/EE for Self-Managed and Dedicated instances affecting all versions from 17.5 prior to 17.6.5, 17.7 prior to 17.7.4, and 17.8 prior to 17.8.2. It was possible for a user added as an External to read and clone internal projects under certain circumstances."

## References
- https://about.gitlab.com/releases/2025/02/12/patch-release-gitlab-17-8-2-released/#saml-authentication-misconfigures-external-user-attribute
- https://gitlab.com/gitlab-org/gitlab/-/issues/512765
- https://nvd.nist.gov/vuln/detail/CVE-2025-1540
