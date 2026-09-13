# [H] BIT-gitlab-2020-13304

## Summary
Severity: High
Advisory: BIT-gitlab-2020-13304
Aliases: CVE-2020-13304
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13304
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.3.0 <13.3.4

## Details
A vulnerability was discovered in GitLab versions before 13.1.10, 13.2.8 and 13.3.4. Same 2 factor Authentication secret code was generated which resulted an attacker to maintain access under certain conditions.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13304.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/27686
- https://hackerone.com/reports/511260
- https://nvd.nist.gov/vuln/detail/CVE-2020-13304
