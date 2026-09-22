# [H] Allowed DELETE on resources on object locked buckets under Governance mode in Minio

## Summary
Severity: High
Advisory: BIT-minio-2023-25812
Aliases: CVE-2023-25812, GHSA-c8fc-mjj8-fc63
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-minio-2023-25812
Type: osv

## Affected
- Bitnami: `minio` — affected >=2020.04.10 <2023.02.17

## Details
Minio is a Multi-Cloud Object Storage framework. Affected versions do not correctly honor a `Deny` policy on ByPassGoverance. Ideally, minio should return "Access Denied" to all users attempting to DELETE a versionId  with the special header `X-Amz-Bypass-Governance-Retention: true`.  However, this was not honored instead the request will be honored and an object under governance would be incorrectly deleted.  All users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/minio/minio/commit/a7188bc9d0f0a5ae05aaf1b8126bcd3cb3fdc485
- https://github.com/minio/minio/pull/16635
- https://github.com/minio/minio/security/advisories/GHSA-c8fc-mjj8-fc63
- https://nvd.nist.gov/vuln/detail/CVE-2023-25812
