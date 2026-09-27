# [M] URLs containing percent-encoded slashes (`/` or `\ `) can trick wcurl into saving the output file...

## Summary
Severity: Medium
Advisory: JLSEC-2026-425
Ecosystem: Julia
CVSS: 4.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-425
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.16.0+0 <8.17.0+0
- Julia: `LibCURL_jll` — affected >=8.15.0+0 <8.17.0+0

## Details
URLs containing percent-encoded slashes (`/` or `\ `) can trick wcurl into
saving the output file outside of the current directory without the user
explicitly asking for it.

This flaw only affects the wcurl command line tool.

## References
- http://www.openwall.com/lists/oss-security/2025/11/04/1
- https://curl.se/docs/CVE-2025-11563.html
- https://curl.se/docs/CVE-2025-11563.json
- https://github.com/advisories/GHSA-6xq2-fm6w-mxfm
- https://lists.debian.org/debian-release/2025/11/msg00504.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-11563
