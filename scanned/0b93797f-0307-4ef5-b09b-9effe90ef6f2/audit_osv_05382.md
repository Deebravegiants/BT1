# [M] Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal') in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-3385
Aliases: CVE-2023-3385
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-3385
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.2.0 <16.2.2

## Details
An issue has been discovered in GitLab affecting all versions starting from 8.10 before 16.0.8, all versions starting from 16.1 before 16.1.3, all versions starting from 16.2 before 16.2.2. Under specific circumstances, a user importing a project 'from export' could access and read unrelated files via uploading a specially crafted file. This was due to a bug in `tar`, fixed in [`tar-1.35`](https://lists.gnu.org/archive/html/info-gnu/2023-07/msg00005.html).

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/416161
- https://hackerone.com/reports/2032730
- https://nvd.nist.gov/vuln/detail/CVE-2023-3385
