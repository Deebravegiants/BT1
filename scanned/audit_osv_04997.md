# [M] BIT-gitlab-2020-26406

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-26406
Aliases: CVE-2020-26406
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-26406
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.5.0 <13.5.2

## Details
Certain SAST CiConfiguration information could be viewed by unauthorized users in GitLab EE starting with 13.3. This information was exposed through GraphQL to non-members of public projects with repository visibility restricted as well as guest members on private projects. Affected versions are: >=13.3, <13.3.9,>=13.4, <13.4.5,>=13.5, <13.5.2.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-26406.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/244921
- https://hackerone.com/reports/965602
- https://nvd.nist.gov/vuln/detail/CVE-2020-26406
