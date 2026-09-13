# [M] BIT-gitlab-2021-39870

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39870
Aliases: CVE-2021-39870
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39870
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.3.0 <14.3.1

## Details
In all versions of GitLab CE/EE since version 11.11, an instance that has the setting to disable Repo by URL import enabled is bypassed by an attacker making a crafted API call.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39870.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/29748
- https://hackerone.com/reports/630263
- https://nvd.nist.gov/vuln/detail/CVE-2021-39870
