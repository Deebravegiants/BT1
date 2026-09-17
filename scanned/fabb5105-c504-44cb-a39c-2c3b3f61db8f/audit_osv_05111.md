# [M] BIT-gitlab-2021-39889

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39889
Aliases: CVE-2021-39889
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39889
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.3.0 <14.3.1

## Details
In all versions of GitLab EE since version 14.1, due to an insecure direct object reference vulnerability, an endpoint may reveal the protected branch name to a malicious user who makes a crafted API call with the ID of the protected branch.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39889.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/338062
- https://hackerone.com/reports/1294017
- https://nvd.nist.gov/vuln/detail/CVE-2021-39889
