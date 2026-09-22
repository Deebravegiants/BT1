# [H] BIT-gitlab-runner-2020-13295

## Summary
Severity: High
Advisory: BIT-gitlab-runner-2020-13295
Aliases: CVE-2020-13295
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-runner-2020-13295
Type: osv

## Affected
- Bitnami: `gitlab-runner` — affected >=13.2.0 <13.2.3

## Details
For GitLab Runner before 13.0.12, 13.1.6, 13.2.3, by replacing dockerd with a malicious server, the Shared Runner is susceptible to SSRF.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13295.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/209096
- https://hackerone.com/reports/809248
- https://nvd.nist.gov/vuln/detail/CVE-2020-13295
