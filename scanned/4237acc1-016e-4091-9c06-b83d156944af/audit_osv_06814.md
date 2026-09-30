# [C] Authentication bypass MinIO Admin API

## Summary
Severity: Critical
Advisory: BIT-minio-2020-11012
Aliases: CVE-2020-11012, GHSA-xv4r-vccv-mg4w
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-minio-2020-11012
Type: osv

## Affected
- Bitnami: `minio` — affected >=0 <2020.04.23

## Details
MinIO versions before RELEASE.2020-04-23T00-58-49Z have an authentication bypass issue in the MinIO admin API. Given an admin access key, it is possible to perform admin API operations i.e. creating new service accounts for existing access keys - without knowing the admin secret key. This has been fixed and released in version RELEASE.2020-04-23T00-58-49Z.

## References
- https://github.com/minio/minio/commit/4cd6ca02c7957aeb2de3eede08b0754332a77923
- https://github.com/minio/minio/pull/9422
- https://github.com/minio/minio/releases/tag/RELEASE.2020-04-23T00-58-49Z
- https://github.com/minio/minio/security/advisories/GHSA-xv4r-vccv-mg4w
- https://nvd.nist.gov/vuln/detail/CVE-2020-11012
