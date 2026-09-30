# [M] BIT-gitlab-2020-13307

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-13307
Aliases: CVE-2020-13307
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13307
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.3.0 <13.3.4

## Details
A vulnerability was discovered in GitLab versions before 13.1.10, 13.2.8 and 13.3.4. GitLab was not revoking current user sessions when 2 factor authentication was activated allowing a malicious user to maintain their access.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13307.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/31307
- https://hackerone.com/reports/676772
- https://nvd.nist.gov/vuln/detail/CVE-2020-13307
