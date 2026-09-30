# [M] BIT-gitlab-2022-2908

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-2908
Aliases: CVE-2022-2908
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2908
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.3.0 <15.3.1

## Details
A potential DoS vulnerability was discovered in Gitlab CE/EE versions starting from 10.7 before 15.1.5, all versions starting from 15.2 before 15.2.3, all versions starting from 15.3 before 15.3.1 allowed an attacker to trigger high CPU usage via a special crafted input added in the Commit message field.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2908.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/363734
- https://hackerone.com/reports/1584156
- https://nvd.nist.gov/vuln/detail/CVE-2022-2908
