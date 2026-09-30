# [M] BIT-gitlab-2022-1545

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-1545
Aliases: CVE-2022-1545
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1545
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.10.0 <14.10.1

## Details
It was possible to disclose details of confidential notes created via the API in Gitlab CE/EE affecting all versions from 13.2 prior to 14.8.6, 14.9 prior to 14.9.4, and 14.10 prior to 14.10.1 if an unauthorised project member was tagged in the note.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1545.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/351030
- https://nvd.nist.gov/vuln/detail/CVE-2022-1545
