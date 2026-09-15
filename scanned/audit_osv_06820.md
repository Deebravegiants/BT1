# [H] Authenticated requests for server update admin API allows path traversal in minio

## Summary
Severity: High
Advisory: BIT-minio-2022-35919
Aliases: CVE-2022-35919, GHSA-gr9v-6pcm-rqvg
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-minio-2022-35919
Type: osv

## Affected
- Bitnami: `minio` — affected >=0 <2022.07.29

## Details
MinIO is a High Performance Object Storage released under GNU Affero General Public License v3.0. In affected versions all 'admin' users authorized for `admin:ServerUpdate` can selectively trigger an error that in response, returns the content of the path requested. Any normal OS system would allow access to contents at any arbitrary paths that are readable by MinIO process. Users are advised to upgrade. Users unable to upgrade may disable ServerUpdate API by denying the `admin:ServerUpdate` action for your admin users via IAM policies.

## References
- http://packetstormsecurity.com/files/175010/Minio-2022-07-29T19-40-48Z-Path-Traversal.html
- https://github.com/minio/minio/commit/bc72e4226e669d98c8e0f3eccc9297be9251c692
- https://github.com/minio/minio/pull/15429
- https://github.com/minio/minio/security/advisories/GHSA-gr9v-6pcm-rqvg
- https://nvd.nist.gov/vuln/detail/CVE-2022-35919
