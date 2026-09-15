# [H] BIT-gitlab-2022-0751

## Summary
Severity: High
Advisory: BIT-gitlab-2022-0751
Aliases: CVE-2022-0751
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0751
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.8.0 <14.8.2

## Details
Inaccurate display of Snippet files containing special characters in all versions of GitLab CE/EE allows an attacker to create Snippets with misleading content which could trick unsuspecting users into executing arbitrary commands

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0751.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/349382
- https://hackerone.com/reports/1420660
- https://nvd.nist.gov/vuln/detail/CVE-2022-0751
