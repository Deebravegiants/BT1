# [M] BIT-gitlab-2021-39873

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39873
Aliases: CVE-2021-39873
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39873
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.3.0 <14.3.1

## Details
In all versions of GitLab CE/EE, there exists a content spoofing vulnerability which may be leveraged by attackers to trick users into visiting a malicious website by spoofing the content in an error response.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39873.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/27241
- https://hackerone.com/reports/504961
- https://nvd.nist.gov/vuln/detail/CVE-2021-39873
