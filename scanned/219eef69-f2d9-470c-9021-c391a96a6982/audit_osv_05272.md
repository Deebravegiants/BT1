# [H] BIT-gitlab-2022-3283

## Summary
Severity: High
Advisory: BIT-gitlab-2022-3283
Aliases: CVE-2022-3283
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3283
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.4.0 <15.4.1

## Details
A potential DOS vulnerability was discovered in GitLab CE/EE affecting all versions before before 15.2.5, all versions starting from 15.3 before 15.3.4, all versions starting from 15.4 before 15.4.1 While cloning an issue with special crafted content added to the description could have been used to trigger high CPU usage.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3283.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/361982
- https://hackerone.com/reports/1543718
- https://nvd.nist.gov/vuln/detail/CVE-2022-3283
