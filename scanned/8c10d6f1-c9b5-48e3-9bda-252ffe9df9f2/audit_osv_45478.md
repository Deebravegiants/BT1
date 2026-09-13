# [H] A vulnerability exists where a new transfer that uses STARTTLS to upgrade the connection might...

## Summary
Severity: High
Advisory: JLSEC-2026-1211
Ecosystem: Julia
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1211
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.21.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.21.0+0

## Details
A vulnerability exists where a new transfer that uses STARTTLS to upgrade the
connection might reuse an existing live connection even though the TLS
configuration mismatches so it should not.

## References
- https://curl.se/docs/CVE-2026-8286.html
- https://curl.se/docs/CVE-2026-8286.json
- https://github.com/advisories/GHSA-32xh-3x3c-6g6h
- https://hackerone.com/reports/3718195
- https://nvd.nist.gov/vuln/detail/CVE-2026-8286
