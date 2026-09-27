# [C] File Browser has risk of HTTP Request/Response smuggling through vulnerable dependency

## Summary
Severity: Critical
Advisory: GHSA-6jqf-mv7m-3q7p
CWE: CWE-1395
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-11-13
Source: https://github.com/advisories/GHSA-6jqf-mv7m-3q7p
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.45.2

## Details
The standard library `net/http` package dependency used by File Browser improperly accepts a bare LF as a line terminator in chunked data chunk-size lines. I can permit request smuggling if a net/http server is used in conjunction with a server that incorrectly accepts a bare LF as part of a chunk-ext.

See https://nvd.nist.gov/vuln/detail/CVE-2025-22871 for more details.

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-6jqf-mv7m-3q7p
- https://nvd.nist.gov/vuln/detail/CVE-2025-22871
- https://github.com/filebrowser/filebrowser
