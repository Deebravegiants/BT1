# [M] BIT-gitlab-2022-3820

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-3820
Aliases: CVE-2022-3820
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3820
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.6.0 <15.6.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 15.4 prior to 15.4.4, and 15.5 prior to 15.5.2. GitLab was not performing correct authentication with some Package Registries when IP address restrictions were configured, allowing an attacker already in possession of a valid Deploy Token to misuse it from any location.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3820.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/378638
- https://nvd.nist.gov/vuln/detail/CVE-2022-3820
