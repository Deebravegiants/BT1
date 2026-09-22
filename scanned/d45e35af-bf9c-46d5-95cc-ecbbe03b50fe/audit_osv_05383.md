# [C] Exposure of Sensitive Information Due to Incompatible Policies in GitLab

## Summary
Severity: Critical
Advisory: BIT-gitlab-2023-3441
Aliases: CVE-2023-3441
Ecosystem: Bitnami
Published: 2024-10-03
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-3441
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=8.0.0 <16.4.0

## Details
An issue has been discovered in GitLab EE/CE affecting all versions starting from 8.0 before 16.4. The product did not sufficiently warn about security implications of granting merge rights to protected branches.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/416482
- https://gitlab.com/gitlab-org/gitlab/-/issues/417284
- https://hackerone.com/reports/2033561
- https://hackerone.com/reports/2041385
- https://nvd.nist.gov/vuln/detail/CVE-2023-3441
