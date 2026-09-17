# [M] BIT-gitlab-2021-39939

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39939
Aliases: CVE-2021-39939
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39939
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.5.0 <14.5.2

## Details
An uncontrolled resource consumption vulnerability in GitLab Runner affecting all versions starting from 13.7 before 14.3.6, all versions starting from 14.4 before 14.4.4, all versions starting from 14.5 before 14.5.2, allows an attacker triggering a job with a specially crafted docker image to exhaust resources on runner manager

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39939.json
- https://gitlab.com/gitlab-org/gitlab-runner/-/issues/28630
- https://nvd.nist.gov/vuln/detail/CVE-2021-39939
