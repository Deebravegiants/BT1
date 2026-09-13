# [H] Bypassing readOnly policy by creating a temporary 'mc share upload' URL

## Summary
Severity: High
Advisory: BIT-minio-2021-21362
Aliases: CVE-2021-21362, GHSA-hq5j-6r98-9m8v
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-minio-2021-21362
Type: osv

## Affected
- Bitnami: `minio` — affected >=0 <2021.03.04

## Details
MinIO is an open-source high performance object storage service and it is API compatible with Amazon S3 cloud storage service. In MinIO before version RELEASE.2021-03-04T00-53-13Z it is possible to bypass a readOnly policy by creating a temporary 'mc share upload' URL. Everyone is impacted who uses MinIO multi-users. This is fixed in version RELEASE.2021-03-04T00-53-13Z. As a workaround, one can disable uploads with `Content-Type: multipart/form-data` as mentioned in the S3 API RESTObjectPOST docs by using a proxy in front of MinIO.

## References
- https://github.com/minio/minio/commit/039f59b552319fcc2f83631bb421a7d4b82bc482
- https://github.com/minio/minio/pull/11682
- https://github.com/minio/minio/releases/tag/RELEASE.2021-03-04T00-53-13Z
- https://github.com/minio/minio/security/advisories/GHSA-hq5j-6r98-9m8v
- https://nvd.nist.gov/vuln/detail/CVE-2021-21362
