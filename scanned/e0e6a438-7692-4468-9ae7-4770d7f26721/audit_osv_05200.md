# [M] BIT-gitlab-2022-1352

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-1352
Aliases: CVE-2022-1352
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1352
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.10.0 <14.10.1

## Details
Due to an insecure direct object reference vulnerability in Gitlab EE/CE affecting all versions from 11.0 prior to 14.8.6, 14.9 prior to 14.9.4, and 14.10 prior to 14.10.1, an endpoint may reveal the issue title to a user who crafted an API call with the ID of the issue from a public project that restricts access to issue only to project members.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1352.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/350691
- https://hackerone.com/reports/1450306
- https://nvd.nist.gov/vuln/detail/CVE-2022-1352
