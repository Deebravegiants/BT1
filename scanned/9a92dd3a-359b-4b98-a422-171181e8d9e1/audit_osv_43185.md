# [M] XAgent Path Traversal Arbitrary File Read via /workspace/file

## Summary
Severity: Medium
Advisory: CVE-2026-72713
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72713
Type: osv

## Details
XAgent contains a path traversal vulnerability in the workspace file endpoint that allows self-registered or default-credential users to read arbitrary files on the host by supplying parent-directory segments in the `file_name` form field with no path containment check. Attackers can register an account without email verification, then submit crafted `file_name` values such as parent-directory traversal sequences to the `/workspace/file` handler to read host files including application secrets, database credentials, and system files outside the Docker sandbox.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72713.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72713
- https://www.vulncheck.com/advisories/xagent-path-traversal-arbitrary-file-read-via-workspace-file
- https://github.com/OpenBMB/XAgent/issues/429
- https://github.com/OpenBMB/XAgent/commit/26f2b6edc75127af524f027c022b382967178e3a
- https://github.com/OpenBMB/XAgent/pull/432
- https://github.com/OpenBMB/XAgent
