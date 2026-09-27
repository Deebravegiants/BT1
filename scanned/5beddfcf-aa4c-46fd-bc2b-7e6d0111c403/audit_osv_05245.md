# [H] BIT-gitlab-2022-2501

## Summary
Severity: High
Advisory: BIT-gitlab-2022-2501
Aliases: CVE-2022-2501
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2501
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.2.0 <15.2.1

## Details
An improper access control issue in GitLab EE affecting all versions from 12.0 prior to 15.0.5, 15.1 prior to 15.1.4, and 15.2 prior to 15.2.1 allows an attacker to bypass IP allow-listing and download artifacts. This attack only bypasses IP allow-listing, proper permissions are still required.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2501.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/364822
- https://hackerone.com/reports/1591412
- https://nvd.nist.gov/vuln/detail/CVE-2022-2501
