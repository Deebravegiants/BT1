# [M] BIT-gitlab-2020-13352

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-13352
Aliases: CVE-2020-13352
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13352
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=0 <13.5.2

## Details
Private group info is leaked leaked in GitLab CE/EE version 10.2 and above, when the project is moved from private to public group. Affected versions are: >=10.2, <13.3.9,>=13.4, <13.4.5,>=13.5, <13.5.2.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13352.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/38281
- https://hackerone.com/reports/748315
- https://nvd.nist.gov/vuln/detail/CVE-2020-13352
