# [H] BIT-gitlab-2022-2498

## Summary
Severity: High
Advisory: BIT-gitlab-2022-2498
Aliases: CVE-2022-2498
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2498
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.2.0 <15.2.1

## Details
An issue in pipeline subscriptions in GitLab EE affecting all versions from 12.8 prior to 15.0.5, 15.1 prior to 15.1.4, and 15.2 prior to 15.2.1 triggered new pipelines with the person who created the tag as the pipeline creator instead of the subscription's author.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2498.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/243703
- https://hackerone.com/reports/966824
- https://nvd.nist.gov/vuln/detail/CVE-2022-2498
