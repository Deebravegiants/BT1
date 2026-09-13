# [C] Cloud Commander before 19.20.2 Directory Traversal via REST and Markdown

## Summary
Severity: Critical
Advisory: CVE-2026-82460
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-29
Source: https://osv.dev/vulnerability/CVE-2026-82460
Type: osv

## Details
Cloud Commander before 19.20.2 contains a directory traversal vulnerability in REST file-operation and markdown endpoints that fails to properly validate path normalization. Attackers can use path traversal sequences to read, write, move, or copy files outside the configured root directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82460.json
- https://github.com/coderaiser/cloudcmd/releases/tag/v19.20.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-82460
- https://www.vulncheck.com/advisories/cloud-commander-before-19.20.2-directory-traversal-via-rest-and-markdown
- https://github.com/coderaiser/cloudcmd/issues/474
- https://github.com/coderaiser/cloudcmd/commit/b9bdc9ed528350eeb2f9ef974c18998096fae919
- https://github.com/coderaiser/cloudcmd
- https://github.com/coderaiser/cloudcmd/blob/v19.20.1/server/root.js
