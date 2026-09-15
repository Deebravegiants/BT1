# [H] Allocation of Resources Without Limits or Throttling in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2023-0121
Aliases: CVE-2023-0121
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-0121
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.0.0 <16.0.2

## Details
A denial of service issue was discovered in GitLab CE/EE affecting all versions starting from 13.2.4 before 15.10.8, all versions starting from 15.11 before 15.11.7, all versions starting from 16.0 before 16.0.2 which allows an attacker to cause high resource consumption using malicious test report artifacts.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-0121.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/387549
- https://hackerone.com/reports/1774688
- https://nvd.nist.gov/vuln/detail/CVE-2023-0121
