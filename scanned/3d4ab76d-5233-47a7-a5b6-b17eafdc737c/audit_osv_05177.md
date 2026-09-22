# [M] BIT-gitlab-2022-0488

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-0488
Aliases: CVE-2022-0488
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0488
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.7.0 <14.7.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting with version 8.10. It was possible to trigger a timeout on a page with markdown by using a specific amount of block-quotes.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0488.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/23520
- https://nvd.nist.gov/vuln/detail/CVE-2022-0488
