# [M] BIT-gitlab-2022-4255

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-4255
Aliases: CVE-2022-4255
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-4255
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.6.0 <15.6.1

## Details
An info leak issue was identified in all versions of GitLab EE from 13.7 prior to 15.4.6, 15.5 prior to 15.5.5, and 15.6 prior to 15.6.1 which exposes user email id through webhook payload.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-4255.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/373819
- https://nvd.nist.gov/vuln/detail/CVE-2022-4255
