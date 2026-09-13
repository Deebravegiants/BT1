# [H] libcurl would wrongly close the same eventfd file descriptor twice when taking down a connection...

## Summary
Severity: High
Advisory: JLSEC-2026-421
Ecosystem: Julia
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-421
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.11.1+0 <8.13.0+0
- Julia: `LibCURL_jll` — affected >=8.11.1+0 <8.12.0+0

## Details
libcurl would wrongly close the same eventfd file descriptor twice when taking
down a connection channel after having completed a threaded name resolve.

## References
- http://www.openwall.com/lists/oss-security/2025/02/05/2
- http://www.openwall.com/lists/oss-security/2025/02/05/5
- https://curl.se/docs/CVE-2025-0665.html
- https://curl.se/docs/CVE-2025-0665.json
- https://github.com/advisories/GHSA-cc57-hgv8-p56r
- https://hackerone.com/reports/2954286
- https://nvd.nist.gov/vuln/detail/CVE-2025-0665
- https://security.netapp.com/advisory/ntap-20250306-0007
- https://security.netapp.com/advisory/ntap-20250306-0007/
