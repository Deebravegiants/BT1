# [M] BIT-gitlab-2021-39884

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39884
Aliases: CVE-2021-39884
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39884
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.3.0 <14.3.1

## Details
In all versions of GitLab EE since version 8.13, an endpoint discloses names of private groups that have access to a project to low privileged users that are part of that project.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39884.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/25414
- https://hackerone.com/reports/447817
- https://nvd.nist.gov/vuln/detail/CVE-2021-39884
