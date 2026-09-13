# [M] When an OAuth2 bearer token is used for an HTTP(S) transfer, and that transfer performs a...

## Summary
Severity: Medium
Advisory: JLSEC-2026-428
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-428
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.20.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.18.0+0

## Details
When an OAuth2 bearer token is used for an HTTP(S) transfer, and that transfer
performs a cross-protocol redirect to a second URL that uses an IMAP, LDAP,
POP3 or SMTP scheme, curl might wrongly pass on the bearer token to the new
target host.

## References
- http://www.openwall.com/lists/oss-security/2026/01/07/4
- https://curl.se/docs/CVE-2025-14524.html
- https://curl.se/docs/CVE-2025-14524.json
- https://github.com/advisories/GHSA-g897-jvjx-78vg
- https://hackerone.com/reports/3459417
- https://nvd.nist.gov/vuln/detail/CVE-2025-14524
