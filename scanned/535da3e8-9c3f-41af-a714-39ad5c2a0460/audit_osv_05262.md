# [C] BIT-gitlab-2022-2992

## Summary
Severity: Critical
Advisory: BIT-gitlab-2022-2992
Aliases: CVE-2022-2992
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2992
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.3.0 <15.3.2

## Details
A vulnerability in GitLab CE/EE affecting all versions from 11.10 prior to 15.1.6, 15.2 to 15.2.4, 15.3 to 15.3.2 allows an authenticated user to achieve remote code execution via the Import from GitHub API endpoint.

## References
- http://packetstormsecurity.com/files/171008/GitLab-GitHub-Repo-Import-Deserialization-Remote-Code-Execution.html
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2992.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/371884
- https://hackerone.com/reports/1679624
- https://nvd.nist.gov/vuln/detail/CVE-2022-2992
