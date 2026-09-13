# [H] BIT-gitlab-2020-13302

## Summary
Severity: High
Advisory: BIT-gitlab-2020-13302
Aliases: CVE-2020-13302
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13302
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.3.0 <13.3.4

## Details
A vulnerability was discovered in GitLab versions before 13.1.10, 13.2.8 and 13.3.4. Under certain conditions GitLab was not properly revoking user sessions and allowed a malicious user to access a user account with an old password.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13302.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/25195
- https://hackerone.com/reports/437194
- https://nvd.nist.gov/vuln/detail/CVE-2020-13302
