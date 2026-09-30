# [H] BIT-gitlab-2022-0741

## Summary
Severity: High
Advisory: BIT-gitlab-2022-0741
Aliases: CVE-2022-0741
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0741
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.8.0 <14.8.2

## Details
Improper input validation in all versions of GitLab CE/EE using sendmail to send emails allowed an attacker to steal environment variables via specially crafted email addresses.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0741.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/337601
- https://hackerone.com/reports/1286317
- https://nvd.nist.gov/vuln/detail/CVE-2022-0741
