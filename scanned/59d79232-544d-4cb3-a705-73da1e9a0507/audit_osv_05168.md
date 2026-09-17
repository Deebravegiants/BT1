# [C] BIT-gitlab-2022-0249

## Summary
Severity: Critical
Advisory: BIT-gitlab-2022-0249
Aliases: CVE-2022-0249
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0249
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.7.0 <14.7.1

## Details
A vulnerability was discovered in GitLab starting with version 12. GitLab was vulnerable to a blind SSRF attack since requests to shared address space were not blocked.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0249.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/29395
- https://hackerone.com/reports/579934
- https://nvd.nist.gov/vuln/detail/CVE-2022-0249
