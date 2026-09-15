# [M] Cleartext Storage of Sensitive Information in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-3950
Aliases: CVE-2023-3950
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-3950
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.3.0 <16.3.1

## Details
An information disclosure issue in GitLab EE affecting all versions from 16.2 prior to 16.2.5, and 16.3 prior to 16.3.1 allowed other Group Owners to see the Public Key for a Google Cloud Logging audit event streaming destination, if configured. Owners can now only write the key, not read it.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/419675
- https://hackerone.com/reports/2079154
- https://nvd.nist.gov/vuln/detail/CVE-2023-3950
