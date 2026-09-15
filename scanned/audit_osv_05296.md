# [C] BIT-gitlab-2022-3726

## Summary
Severity: Critical
Advisory: BIT-gitlab-2022-3726
Aliases: CVE-2022-3726
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3726
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.5.0 <15.5.2

## Details
Lack of sand-boxing of OpenAPI documents in GitLab CE/EE affecting all versions from 12.6 prior to 15.3.5, 15.4 prior to 15.4.4, and 15.5 prior to 15.5.2 allows an attacker to trick a user to click on the Swagger OpenAPI viewer and issue HTTP requests that affect the victim's account.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3726.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/362509
- https://hackerone.com/reports/1563383
- https://nvd.nist.gov/vuln/detail/CVE-2022-3726
