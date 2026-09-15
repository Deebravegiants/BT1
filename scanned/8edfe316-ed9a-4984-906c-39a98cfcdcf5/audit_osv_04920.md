# [M] BIT-gitlab-2020-13268

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-13268
Aliases: CVE-2020-13268
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13268
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.0.0 <13.0.1

## Details
A specially crafted request could be used to confirm the existence of files hosted on object storage services, without disclosing their contents. This vulnerability affects GitLab CE/EE 12.10 and later through 13.0.1

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13268.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/214220
- https://hackerone.com/reports/848415
- https://nvd.nist.gov/vuln/detail/CVE-2020-13268
