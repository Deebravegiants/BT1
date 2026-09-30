# [H] BIT-gitlab-2022-1413

## Summary
Severity: High
Advisory: BIT-gitlab-2022-1413
Aliases: CVE-2022-1413
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1413
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.10.0 <14.10.1

## Details
Missing input masking in GitLab CE/EE affecting all versions starting from 1.0.2 before 14.8.6, all versions from 14.9.0 before 14.9.4, and all versions from 14.10.0 before 14.10.1 causes potentially sensitive integration properties to be disclosed in the web interface

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1413.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/353720
- https://nvd.nist.gov/vuln/detail/CVE-2022-1413
