# [M] CVE-2026-7869

## Summary
Severity: Medium
Advisory: CVE-2026-7869
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-7869
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.10.3 is vulnerable to Path Traversal in the Knowledge Bases API (`POST /api/v1/knowledge_bases`). This occurs because user-supplied knowledge base names are used directly to create file paths without proper sanitization or containment checks. An authenticated attacker can exploit this flaw to create directories and write files anywhere on the server's filesystem.

## References
- https://www.ibm.com/support/pages/node/7282647
