# [M] BIT-gitlab-2022-0090

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-0090
Aliases: CVE-2022-0090
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0090
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.6.0 <14.6.1

## Details
An issue has been discovered affecting GitLab versions prior to 14.4.5, between 14.5.0 and 14.5.3, and between 14.6.0 and 14.6.1. GitLab is configured in a way that it doesn't ignore replacement references with git sub-commands, allowing a malicious user to spoof the contents of their commits in the UI.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0090.json
- https://gitlab.com/gitlab-org/gitaly/-/issues/3948
- https://hackerone.com/reports/1415964
- https://nvd.nist.gov/vuln/detail/CVE-2022-0090
