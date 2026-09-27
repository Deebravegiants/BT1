# [H] BIT-gitlab-2020-13355

## Summary
Severity: High
Advisory: BIT-gitlab-2020-13355
Aliases: CVE-2020-13355
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13355
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=0 <13.5.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 8.14. A path traversal is found in LFS Upload that allows attacker to overwrite certain specific paths on the server. Affected versions are: >=8.14, <13.3.9,>=13.4, <13.4.5,>=13.5, <13.5.2.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13355.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/255886
- https://hackerone.com/reports/990800
- https://nvd.nist.gov/vuln/detail/CVE-2020-13355
