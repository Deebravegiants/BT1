# [M] BIT-gitlab-2021-39871

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39871
Aliases: CVE-2021-39871
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39871
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.3.0 <14.3.1

## Details
In all versions of GitLab CE/EE since version 13.0, an instance that has the setting to disable Bitbucket Server import enabled is bypassed by an attacker making a crafted API call.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39871.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/340782
- https://hackerone.com/reports/630263
- https://nvd.nist.gov/vuln/detail/CVE-2021-39871
