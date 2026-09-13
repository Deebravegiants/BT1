# [C] libcurl had a flaw that when instructed to clear proxy authentication credentials which made it...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1218
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1218
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.9.0+0 <8.21.0+0
- Julia: `LibCURL_jll` — affected >=8.8.0+0 <8.21.0+0

## Details
libcurl had a flaw that when instructed to clear proxy authentication
credentials which made it not do so, leaving the old credentials around to get
used for subsequent transfers that should not know nor use them.

## References
- https://curl.se/docs/CVE-2026-9079.html
- https://curl.se/docs/CVE-2026-9079.json
- https://github.com/advisories/GHSA-f4cv-xm48-3694
- https://hackerone.com/reports/3750295
- https://nvd.nist.gov/vuln/detail/CVE-2026-9079
