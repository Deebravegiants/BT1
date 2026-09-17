# [H] Improper Certificate Validation in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2023-6680
Aliases: CVE-2023-6680
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-6680
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.6.0 <16.6.2

## Details
An improper certificate validation issue in Smartcard authentication in GitLab EE affecting all versions from 11.6 prior to 16.4.4, 16.5 prior to 16.5.4, and 16.6 prior to 16.6.2 allows an attacker to authenticate as another user given their public key if they use Smartcard authentication. Smartcard authentication is an experimental feature and has to be manually enabled by an administrator.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/421607
- https://nvd.nist.gov/vuln/detail/CVE-2023-6680
