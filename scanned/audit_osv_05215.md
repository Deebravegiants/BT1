# [M] BIT-gitlab-2022-1936

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-1936
Aliases: CVE-2022-1936
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1936
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.0.0 <15.0.1

## Details
Incorrect authorization in GitLab EE affecting all versions from 12.0 before 14.9.5, all versions starting from 14.10 before 14.10.4, all versions starting from 15.0 before 15.0.1 allowed an attacker already in possession of a valid Project Deploy Token to misuse it from any location even when IP address restrictions were configured

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1936.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/363638
- https://nvd.nist.gov/vuln/detail/CVE-2022-1936
