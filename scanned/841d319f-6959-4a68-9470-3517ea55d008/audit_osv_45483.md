# [H] libcurl would reuse a previously created connection even when some mTLS config related option had...

## Summary
Severity: High
Advisory: JLSEC-2026-1217
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1217
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.21.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.21.0+0

## Details
libcurl would reuse a previously created connection even when some mTLS config
related option had been changed that should have prohibited reuse.

libcurl keeps previously used connections in a connection pool for subsequent
transfers to reuse if one of them matches the setup. However, some TLS
settings related to client certificates were left out from the configuration
match checks, making them match too easily. In particular options related to
the private key.

## References
- https://curl.se/docs/CVE-2026-8932.html
- https://curl.se/docs/CVE-2026-8932.json
- https://github.com/advisories/GHSA-m7xm-hf59-w6rj
- https://hackerone.com/reports/3733910
- https://nvd.nist.gov/vuln/detail/CVE-2026-8932
