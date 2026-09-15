# [M] A vulnerability exists where a connection requiring TLS incorrectly reuses an existing...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1203
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1203
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.20.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.20.0+0

## Details
A vulnerability exists where a connection requiring TLS incorrectly reuses an
existing unencrypted connection from the same connection pool. If an initial
transfer is made in clear-text (via IMAP, SMTP, or POP3), a subsequent request
to that same host bypasses the TLS requirement and instead transmit data
unencrypted.

## References
- http://www.openwall.com/lists/oss-security/2026/04/29/7
- https://curl.se/docs/CVE-2026-4873.html
- https://curl.se/docs/CVE-2026-4873.json
- https://github.com/advisories/GHSA-5fgw-rv54-prjx
- https://hackerone.com/reports/3621851
- https://nvd.nist.gov/vuln/detail/CVE-2026-4873
