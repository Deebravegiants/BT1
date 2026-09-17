# [H] BIT-gitlab-2022-2533

## Summary
Severity: High
Advisory: BIT-gitlab-2022-2533
Aliases: CVE-2022-2533
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2533
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.3.0 <15.3.2

## Details
An issue has been discovered in GitLab affecting all versions starting from 12.10 before 15.1.6, all versions starting from 15.2 before 15.2.4, all versions starting from 15.3 before 15.3.2. GitLab was not performing correct authentication with some Package Registries when IP address restrictions were configured, allowing an attacker already in possession of a valid Deploy Token to misuse it from any location.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2533.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/363863
- https://nvd.nist.gov/vuln/detail/CVE-2022-2533
