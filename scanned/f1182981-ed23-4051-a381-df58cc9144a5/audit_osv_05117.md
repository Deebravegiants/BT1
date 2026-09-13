# [M] BIT-gitlab-2021-39895

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39895
Aliases: CVE-2021-39895
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39895
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.3.0 <14.3.1

## Details
In all versions of GitLab CE/EE since version 8.0, an attacker can set the pipeline schedules to be active in a project export so when an unsuspecting owner imports that project, pipelines are active by default on that project. Under specialized conditions, this may lead to information disclosure if the project is imported from an untrusted source.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39895.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/337824
- https://hackerone.com/reports/1272535
- https://nvd.nist.gov/vuln/detail/CVE-2021-39895
