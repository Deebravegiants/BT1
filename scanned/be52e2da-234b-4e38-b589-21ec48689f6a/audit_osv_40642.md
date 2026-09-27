# [H] OpenChamber 1.11.7 Path Traversal File Read via allowOutsideWorkspace Parameter

## Summary
Severity: High
Advisory: CVE-2026-53976
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-53976
Type: osv

## Details
OpenChamber 1.11.7 contains a path traversal vulnerability in the file-serving endpoints /api/fs/read, /api/fs/stat, and /api/fs/raw that allows unauthenticated remote attackers to read arbitrary files by supplying the allowOutsideWorkspace=true query parameter alongside an absolute path, bypassing the workspace boundary check in resolveReadPathFromContext. Attackers can exploit the vacuous isPathWithinRoot guard to read sensitive files such as the JWT signing secret, SSH private keys, API credentials, and environment variables, enabling full authentication bypass by forging session cookies on password-protected deployments.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53976.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53976
- https://www.vulncheck.com/advisories/openchamber-path-traversal-file-read-via-allowoutsideworkspace-parameter
- https://github.com/openchamber/openchamber/commit/f1b9506132faf6c564a2694c7f33b94421a49b4a
- https://github.com/openchamber/openchamber
