# [H] incomplete mTLS config matching in conn reuse

## Summary
Severity: High
Advisory: CVE-2026-8932
Aliases: CURL-CVE-2026-8932
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-8932
Type: osv

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
- https://hackerone.com/reports/3733910
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8932.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8932
