# [H] SeaweedFS: Authenticated S3 object-scope bypass in PutObjectAcl allows overwriting a different object with the same basename

## Summary
Severity: High
Advisory: BIT-seaweedfs-2026-77611
Aliases: CVE-2026-77611, GHSA-9x53-cjpr-m682
Ecosystem: Bitnami
Published: 2026-09-02
Source: https://osv.dev/vulnerability/BIT-seaweedfs-2026-77611
Type: osv

## Affected
- Bitnami: `seaweedfs` — affected >=0 <4.40.0

## Details
SeaweedFS is a distributed storage system for files and blobs. In versions prior to 4.40, an authenticated S3 principal with permissions scoped to a nested object key can overwrite a different object outside that scope by calling PutObjectAcl on the key it is allowed to access. The handler authorizes the request against the requested nested key but then writes the updated entry back to the bucket root rather than the key's actual parent directory, so an ACL change on allowed/protected.txt is instead applied to protected.txt at the bucket root. Because the update carries the full entry rather than only ACL metadata, an existing target object is overwritten with the content, metadata, owner information, and ACL of the scoped object, bypassing the object-level action scoping configured through the static S3 identity file. This issue is fixed in version 4.40.

## References
- https://github.com/seaweedfs/seaweedfs/commit/311bc3a6dfbd042751692bc3de8accc516fcf8c1
- https://github.com/seaweedfs/seaweedfs/security/advisories/GHSA-9x53-cjpr-m682
- https://nvd.nist.gov/vuln/detail/CVE-2026-77611
