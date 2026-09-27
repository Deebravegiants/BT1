# [H] When doing a second SMB request to the same host again, curl would wrongly use a data pointer...

## Summary
Severity: High
Advisory: JLSEC-2026-439
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-439
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.13.0+0 <8.20.0+0
- Julia: `LibCURL_jll` — affected >=8.13.0+0 <8.19.0+0

## Details
When doing a second SMB request to the same host again, curl would wrongly use
a data pointer pointing into already freed memory.

## References
- http://www.openwall.com/lists/oss-security/2026/03/11/4
- https://curl.se/docs/CVE-2026-3805.html
- https://curl.se/docs/CVE-2026-3805.json
- https://github.com/advisories/GHSA-2289-hhfc-p684
- https://hackerone.com/reports/3591944
- https://nvd.nist.gov/vuln/detail/CVE-2026-3805
