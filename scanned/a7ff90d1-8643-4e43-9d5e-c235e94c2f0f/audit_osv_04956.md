# [H] BIT-gitlab-2020-13315

## Summary
Severity: High
Advisory: BIT-gitlab-2020-13315
Aliases: CVE-2020-13315
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13315
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.3.0 <13.3.4

## Details
A vulnerability was discovered in GitLab versions before 13.1.10, 13.2.8 and 13.3.4. The profile activity page was not restricting the amount of results one could request, potentially resulting in a denial of service.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13315.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/25825
- https://hackerone.com/reports/463010
- https://nvd.nist.gov/vuln/detail/CVE-2020-13315
