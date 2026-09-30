# [M] BIT-gitlab-2021-39927

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39927
Aliases: CVE-2021-39927
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39927
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.6.0 <14.6.2

## Details
Server side request forgery protections in GitLab CE/EE versions between 8.4 and 14.4.4, between 14.5.0 and 14.5.2, and between 14.6.0 and 14.6.1 would fail to protect against attacks sending requests to localhost on port 80 or 443 if GitLab was configured to run on a port other than 80 or 443

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39927.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/340476
- https://nvd.nist.gov/vuln/detail/CVE-2021-39927
