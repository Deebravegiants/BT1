# [H] BIT-gitlab-2022-0427

## Summary
Severity: High
Advisory: BIT-gitlab-2022-0427
Aliases: CVE-2022-0427
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0427
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.7.0 <14.7.1

## Details
Missing sanitization of HTML attributes in Jupyter notebooks in all versions of GitLab CE/EE since version 14.5 allows an attacker to perform arbitrary HTTP POST requests on a user's behalf leading to potential account takeover

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0427.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/347284
- https://hackerone.com/reports/1409788
- https://nvd.nist.gov/vuln/detail/CVE-2022-0427
