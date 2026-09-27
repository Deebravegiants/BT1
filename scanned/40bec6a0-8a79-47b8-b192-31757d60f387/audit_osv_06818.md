# [H] Improper Privilege Management in MinIO

## Summary
Severity: High
Advisory: BIT-minio-2022-24842
Aliases: CVE-2022-24842, GHSA-2j69-jjmg-534q
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-minio-2022-24842
Type: osv

## Affected
- Bitnami: `minio` — affected >=2021.12.09 <2022.04.12

## Details
MinIO is a High Performance Object Storage released under GNU Affero General Public License v3.0. A security issue was found where an non-admin user is able to create service accounts for root or other admin users and then is able to assume their access policies via the generated credentials. This in turn allows the user to escalate privilege to that of the root user. This vulnerability has been resolved in pull request #14729 and is included in `RELEASE.2022-04-12T06-55-35Z`. Users unable to upgrade may workaround this issue by explicitly adding a `admin:CreateServiceAccount` deny policy, however, this, in turn, denies the user the ability to create their own service accounts as well.

## References
- https://github.com/minio/minio/commit/66b14a0d32684d527ae8018dc6d9d46ccce58ae3
- https://github.com/minio/minio/pull/14729
- https://github.com/minio/minio/security/advisories/GHSA-2j69-jjmg-534q
- https://nvd.nist.gov/vuln/detail/CVE-2022-24842
