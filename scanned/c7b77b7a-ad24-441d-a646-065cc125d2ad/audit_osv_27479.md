# [C] Path Traversal and Arbitrary File Upload Vulnerability in qdrant/qdrant

## Summary
Severity: Critical
Advisory: CVE-2024-2221
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2024-2221
Type: osv

## Details
qdrant/qdrant is vulnerable to a path traversal and arbitrary file upload vulnerability via the `/collections/{COLLECTION}/snapshots/upload` endpoint, specifically through the `snapshot` parameter. This vulnerability allows attackers to upload and overwrite any file on the filesystem, leading to potential remote code execution. This issue affects the integrity and availability of the system, enabling unauthorized access and potentially causing the server to malfunction.

## References
- https://huntr.com/bounties/6be8d4e3-67e6-4660-a8db-04215a1cff3e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2221.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2221
- https://github.com/qdrant/qdrant/commit/e6411907f0ecf3c2f8ba44ab704b9e4597d9705d
