# [M] Vanna 2.0.2 Path Traversal via FileSystemConversationStore

## Summary
Severity: Medium
Advisory: CVE-2026-65702
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-65702
Type: osv

## Details
Vanna through 2.0.2 contains a path traversal vulnerability in the FileSystemConversationStore persistence integration that allows unauthenticated remote attackers to write attacker-controlled JSON files to arbitrary filesystem locations and read conversation metadata from outside the intended store base directory. Attackers can supply path traversal sequences in the conversation_id parameter submitted to the unauthenticated chat API endpoints to escape the base directory during both write and read operations, enabling arbitrary file write with attacker-controlled content and unauthorized file read on the server filesystem.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65702.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65702
- https://www.vulncheck.com/advisories/vanna-path-traversal-via-filesystemconversationstore
- https://github.com/vanna-ai/vanna
- https://github.com/geo-chen/oss/blob/main/vanna.md
