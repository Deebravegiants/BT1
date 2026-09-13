# [M] Incorrect Privilege Assignment in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-2485
Aliases: CVE-2023-2485
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-2485
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.0.0 <16.0.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 14.1 before 15.10.8, all versions starting from 15.11 before 15.11.7, all versions starting from 16.0 before 16.0.2. A malicious maintainer in a project can escalate other users to Owners in that project if they import members from another project that those other users are Owners of.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-2485.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/407830
- https://hackerone.com/reports/1934811
- https://nvd.nist.gov/vuln/detail/CVE-2023-2485
