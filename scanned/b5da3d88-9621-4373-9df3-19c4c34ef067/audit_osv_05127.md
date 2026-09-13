# [M] BIT-gitlab-2021-39909

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39909
Aliases: CVE-2021-39909
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39909
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.4.0 <14.4.1

## Details
Lack of email address ownership verification in the CODEOWNERS feature in all versions of GitLab EE starting from 11.3 before 14.2.6, all versions starting from 14.3 before 14.3.4, and all versions starting from 14.4 before 14.4.1 allows an attacker to bypass CODEOWNERS Merge Request approval requirement under rare circumstances

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39909.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/335191
- https://hackerone.com/reports/1237750
- https://nvd.nist.gov/vuln/detail/CVE-2021-39909
