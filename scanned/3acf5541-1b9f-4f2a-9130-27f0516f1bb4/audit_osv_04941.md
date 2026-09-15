# [H] BIT-gitlab-2020-13299

## Summary
Severity: High
Advisory: BIT-gitlab-2020-13299
Aliases: CVE-2020-13299
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13299
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.3.0 <13.3.4

## Details
A vulnerability was discovered in GitLab versions before 13.1.10, 13.2.8 and 13.3.4. The revocation feature was not revoking all session tokens and one could re-use it to obtain a valid session.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13299.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/222508
- https://hackerone.com/reports/896225
- https://nvd.nist.gov/vuln/detail/CVE-2020-13299
