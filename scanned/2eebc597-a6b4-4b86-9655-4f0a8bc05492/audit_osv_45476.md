# [M] When curl is told to use the Certificate Status Request TLS extension, often referred to as *OCSP...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1209
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1209
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.17.0+0 <8.20.0+0
- Julia: `LibCURL_jll` — affected >=8.17.0+0 <8.20.0+0

## Details
When curl is told to use the Certificate Status Request TLS extension, often
referred to as *OCSP stapling*, to verify that the server certificate is
valid, it fails to detect OCSP problems and instead wrongly consider the
response as fine.

## References
- http://www.openwall.com/lists/oss-security/2026/04/29/12
- https://curl.se/docs/CVE-2026-7009.html
- https://curl.se/docs/CVE-2026-7009.json
- https://github.com/advisories/GHSA-v355-7mqg-qj9c
- https://hackerone.com/reports/3694390
- https://nvd.nist.gov/vuln/detail/CVE-2026-7009
