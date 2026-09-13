# [M] BIT-gitlab-2020-26414

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-26414
Aliases: CVE-2020-26414
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-26414
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.7.0 <13.7.2

## Details
An issue has been discovered in GitLab affecting all versions starting from 12.4. The regex used for package names is written in a way that makes execution time have quadratic growth based on the length of the malicious input string.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-26414.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/270199
- https://nvd.nist.gov/vuln/detail/CVE-2020-26414
