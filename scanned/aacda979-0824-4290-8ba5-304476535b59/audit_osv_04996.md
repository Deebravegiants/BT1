# [H] BIT-gitlab-2020-26405

## Summary
Severity: High
Advisory: BIT-gitlab-2020-26405
Aliases: CVE-2020-26405
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-26405
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=0 <13.5.2

## Details
Path traversal vulnerability in package upload functionality in GitLab CE/EE starting from 12.8 allows an attacker to save packages in arbitrary locations. Affected versions are >=12.8, <13.3.9,>=13.4, <13.4.5,>=13.5, <13.5.2.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-26405.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/247371
- https://hackerone.com/reports/835427
- https://nvd.nist.gov/vuln/detail/CVE-2020-26405
