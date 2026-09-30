# [H] BIT-gitlab-2022-2931

## Summary
Severity: High
Advisory: BIT-gitlab-2022-2931
Aliases: CVE-2022-2931
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2931
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.3.0 <15.3.2

## Details
A potential DOS vulnerability was discovered in GitLab CE/EE affecting all versions before 15.1.6, all versions starting from 15.2 before 15.2.4, all versions starting from 15.3 before 15.3.2. Malformed content added to the issue description could have been used to trigger high CPU usage.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2931.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/361982
- https://hackerone.com/reports/1543718
- https://nvd.nist.gov/vuln/detail/CVE-2022-2931
