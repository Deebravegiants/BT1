# [M] BIT-gitlab-2020-13310

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-13310
Aliases: CVE-2020-13310
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13310
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.3.0 <13.3.1

## Details
A vulnerability was discovered in GitLab runner versions before 13.1.3, 13.2.3 and 13.3.1. It was possible to make the gitlab-runner process crash by sending malformed queries, resulting in a denial of service.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13310.json
- https://gitlab.com/gitlab-org/gitlab-runner/-/issues/25857
- https://gitlab.com/gitlab-org/gitlab-runner/-/issues/26819
- https://nvd.nist.gov/vuln/detail/CVE-2020-13310
