# [H] BIT-gitlab-2022-1174

## Summary
Severity: High
Advisory: BIT-gitlab-2022-1174
Aliases: CVE-2022-1174
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1174
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.9.0 <14.9.2

## Details
A potential DoS vulnerability was discovered in Gitlab CE/EE versions 13.7 before 14.7.7, all versions starting from 14.8 before 14.8.5, all versions starting from 14.9 before 14.9.2 allowed an attacker to trigger high CPU usage via a special crafted input added in Issues, Merge requests, Milestones, Snippets, Wiki pages, etc.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1174.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/338721
- https://hackerone.com/reports/1305431
- https://nvd.nist.gov/vuln/detail/CVE-2022-1174
