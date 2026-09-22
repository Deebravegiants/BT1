# [M] BIT-gitlab-2020-26416

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-26416
Aliases: CVE-2020-26416
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-26416
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.6.0 <13.6.2

## Details
Information disclosure in Advanced Search component of GitLab EE starting from 8.4 results in exposure of search terms via Rails logs. This affects versions >=8.4 to <13.4.7, >=13.5 to <13.5.5, and >=13.6 to <13.6.2.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-26416.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/244495
- https://nvd.nist.gov/vuln/detail/CVE-2020-26416
