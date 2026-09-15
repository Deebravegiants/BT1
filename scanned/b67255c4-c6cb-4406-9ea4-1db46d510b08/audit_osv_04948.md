# [H] BIT-gitlab-2020-13306

## Summary
Severity: High
Advisory: BIT-gitlab-2020-13306
Aliases: CVE-2020-13306
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13306
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.3.0 <13.3.4

## Details
A vulnerability was discovered in GitLab versions before 13.1.10, 13.2.8 and 13.3.4. GitLab Webhook feature could be abused to perform denial of service attacks due to the lack of rate limitation.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13306.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/223681
- https://hackerone.com/reports/904134
- https://nvd.nist.gov/vuln/detail/CVE-2020-13306
