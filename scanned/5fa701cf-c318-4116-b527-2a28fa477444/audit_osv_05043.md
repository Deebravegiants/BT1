# [C] BIT-gitlab-2021-22205

## Summary
Severity: Critical
Advisory: BIT-gitlab-2021-22205
Aliases: CVE-2021-22205
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22205
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.10.0 <13.10.3

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 11.9. GitLab was not properly validating image files that were passed to a file parser which resulted in a remote command execution.

## References
- http://packetstormsecurity.com/files/164768/GitLab-Unauthenticated-Remote-ExifTool-Command-Injection.html
- http://packetstormsecurity.com/files/164994/GitLab-13.10.2-Remote-Code-Execution.html
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22205.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/327121
- https://hackerone.com/reports/1154542
- https://nvd.nist.gov/vuln/detail/CVE-2021-22205
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2021-22205
