# [M] BIT-gitlab-2020-13351

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-13351
Aliases: CVE-2020-13351
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13351
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=0 <13.5.2

## Details
Insufficient permission checks in scheduled pipeline API in GitLab CE/EE 13.0+ allows an attacker to read variable names and values for scheduled pipelines on projects visible to the attacker. Affected versions are >=13.0, <13.3.9,>=13.4.0, <13.4.5,>=13.5.0, <13.5.2.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13351.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/239369
- https://hackerone.com/reports/962462
- https://nvd.nist.gov/vuln/detail/CVE-2020-13351
