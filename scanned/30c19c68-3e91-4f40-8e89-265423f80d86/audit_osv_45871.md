# [M] When doing multi-threaded LDAPS transfers (LDAP over TLS) with libcurl, changing TLS options in one...

## Summary
Severity: Medium
Advisory: JLSEC-2026-427
Ecosystem: Julia
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-427
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.20.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.18.0+0

## Details
When doing multi-threaded LDAPS transfers (LDAP over TLS) with libcurl,
changing TLS options in one thread would inadvertently change them globally
and therefore possibly also affect other concurrently setup transfers.

Disabling certificate verification for a specific transfer could
unintentionally disable the feature for other threads as well.

## References
- http://www.openwall.com/lists/oss-security/2026/01/07/3
- https://curl.se/docs/CVE-2025-14017.html
- https://curl.se/docs/CVE-2025-14017.json
- https://github.com/advisories/GHSA-jh4h-2cg6-889h
- https://nvd.nist.gov/vuln/detail/CVE-2025-14017
