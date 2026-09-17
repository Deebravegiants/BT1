# [M] BIT-gitlab-2021-22223

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22223
Aliases: CVE-2021-22223
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22223
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.0.0 <14.0.2

## Details
Client-Side code injection through Feature Flag name in GitLab CE/EE starting with 11.9 allows a specially crafted feature flag name to PUT requests on behalf of other users via clicking on a link

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22223.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/293946
- https://hackerone.com/reports/1059557
- https://nvd.nist.gov/vuln/detail/CVE-2021-22223
