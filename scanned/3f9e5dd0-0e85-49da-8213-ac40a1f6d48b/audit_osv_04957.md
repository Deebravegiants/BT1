# [M] BIT-gitlab-2020-13316

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-13316
Aliases: CVE-2020-13316
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13316
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.3.0 <13.3.4

## Details
A vulnerability was discovered in GitLab versions before 13.1.10, 13.2.8 and 13.3.4. GitLab was not validating a Deploy-Token and allowed a disabled repository be accessible via a git command line.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13316.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/220137
- https://hackerone.com/reports/884174
- https://nvd.nist.gov/vuln/detail/CVE-2020-13316
