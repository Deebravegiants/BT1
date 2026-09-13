# [C] BIT-gitlab-2020-13300

## Summary
Severity: Critical
Advisory: BIT-gitlab-2020-13300
Aliases: CVE-2020-13300
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13300
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.3.0 <13.3.4

## Details
GitLab CE/EE version 13.3 prior to 13.3.4 was vulnerable to an OAuth authorization scope change without user consent in the middle of the authorization flow.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13300.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/219931
- https://hackerone.com/reports/884766
- https://nvd.nist.gov/vuln/detail/CVE-2020-13300
