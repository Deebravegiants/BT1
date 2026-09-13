# [M] GNU Wget through 1.25.0, fixed in commit 43d3ba9, contains an integer overflow vulnerability in...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1159
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1159
Type: osv

## Affected
- Julia: `wget_jll` — affected unspecified

## Details
GNU Wget through 1.25.0, fixed in commit 43d3ba9, contains an integer overflow vulnerability in the `parse_content_range()` function within `src/http.c` that allows server-controlled values to cause signed integer arithmetic to overflow. Attackers can supply malicious Content-Range header values to trigger undefined behavior and download desynchronization in the affected client.

## References
- https://github.com/advisories/GHSA-5f52-px6m-c5hw
- https://gitlab.com/gnuwget/wget/-/commit/43d3ba9336bc94937e6fae2365c6ffd30c34ffcf
- https://nvd.nist.gov/vuln/detail/CVE-2026-58470
- https://www.vulncheck.com/advisories/gnu-wget-integer-overflow-via-content-range-header-parsing
