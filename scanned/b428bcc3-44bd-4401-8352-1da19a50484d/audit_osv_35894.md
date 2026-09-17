# [H] osim: Path Traversal via query parameters in Nginx configuration

## Summary
Severity: High
Advisory: CVE-2026-1616
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-01-29
Source: https://osv.dev/vulnerability/CVE-2026-1616
Type: osv

## Details
The $uri$args concatenation in nginx configuration file present in Open Security Issue Management (OSIM) prior v2025.9.0 allows path traversal attacks via query parameters.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/1xxx/CVE-2026-1616.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-1616
- https://github.com/RedHatProductSecurity/osim/pull/615
- https://github.com/RedHatProductSecurity/osim
