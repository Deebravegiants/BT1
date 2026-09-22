# [H] BIT-gitlab-2022-1423

## Summary
Severity: High
Advisory: BIT-gitlab-2022-1423
Aliases: CVE-2022-1423
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1423
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.10.0 <14.10.1

## Details
Improper access control in the CI/CD cache mechanism in GitLab CE/EE affecting all versions starting from 1.0.2 before 14.8.6, all versions from 14.9.0 before 14.9.4, and all versions from 14.10.0 before 14.10.1 allows a malicious actor with Developer privileges to perform cache poisoning leading to arbitrary code execution in protected branches

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1423.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/330047
- https://hackerone.com/reports/1182375
- https://nvd.nist.gov/vuln/detail/CVE-2022-1423
