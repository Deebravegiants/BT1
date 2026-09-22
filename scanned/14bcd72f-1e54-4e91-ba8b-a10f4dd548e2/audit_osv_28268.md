# [M] Qdrant Full Snapshot REST API snapshots.rs path traversal

## Summary
Severity: Medium
Advisory: CVE-2024-3078
CVSS: 5.5 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-03-29
Source: https://osv.dev/vulnerability/CVE-2024-3078
Type: osv

## Details
A vulnerability was found in Qdrant up to 1.6.1/1.7.4/1.8.2 and classified as critical. This issue affects some unknown processing of the file lib/collection/src/collection/snapshots.rs of the component Full Snapshot REST API. The manipulation leads to path traversal. Upgrading to version 1.8.3 is able to address this issue. The patch is named 3ab5172e9c8f14fa1f7b24e7147eac74e2412b62. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-258611.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3078.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3078
- https://vuldb.com/?id.258611
- https://github.com/qdrant/qdrant/pull/3856
- https://vuldb.com/?ctiid.258611
- https://github.com/qdrant/qdrant/commit/3ab5172e9c8f14fa1f7b24e7147eac74e2412b62
- https://github.com/qdrant/qdrant/releases/tag/v1.8.3
