# [M] BIT-gitlab-2022-1983

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-1983
Aliases: CVE-2022-1983
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1983
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.1.0 <15.1.1

## Details
Incorrect authorization in GitLab EE affecting all versions from 10.7 prior to 14.10.5, 15.0 prior to 15.0.4, and 15.1 prior to 15.1.1, allowed an attacker already in possession of a valid Deploy Key or a Deploy Token to misuse it from any location to access Container Registries even when IP address restrictions were configured.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1983.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/363651
- https://nvd.nist.gov/vuln/detail/CVE-2022-1983
