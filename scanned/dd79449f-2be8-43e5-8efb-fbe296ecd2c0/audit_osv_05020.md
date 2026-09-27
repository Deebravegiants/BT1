# [M] BIT-gitlab-2021-22177

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22177
Aliases: CVE-2021-22177
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22177
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.8.0 <13.8.4

## Details
Potential DoS was identified in gitlab-shell in GitLab CE/EE version 12.6.0 or above, which allows an attacker to spike the server resource utilization via gitlab-shell command.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22177.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/238988
- https://hackerone.com/reports/953444
- https://nvd.nist.gov/vuln/detail/CVE-2021-22177
