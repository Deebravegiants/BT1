# [M] CVE-2026-7646

## Summary
Severity: Medium
Advisory: CVE-2026-7646
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-7646
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.10.3 allows users to read arbitrary files from the server filesystem, including other users' uploaded documents, the JWT signing secret, the SQLite database, and process environment variables, by sending a crafted MCP `resources/read` request with a URL-encoded path traversal sequence in the filename.

## References
- https://www.ibm.com/support/pages/node/7282147
