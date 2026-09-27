# [C] Successfully using libcurl to do a transfer to a specific HTTP origin (`hostA`) with **Digest**...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1201
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1201
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.21.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.21.0+0

## Details
Successfully using libcurl to do a transfer to a specific HTTP origin
(`hostA`) with **Digest** authentication and then changing the origin to a
different one (`hostB`) for a second transfer, reusing the same handle, makes
libcurl wrongly pass on the  `Authorization:` header field meant for `hostA`,
to `hostB`.

## References
- https://curl.se/docs/CVE-2026-11856.html
- https://curl.se/docs/CVE-2026-11856.json
- https://github.com/advisories/GHSA-9crq-qh8v-6xmm
- https://hackerone.com/reports/3793260
- https://nvd.nist.gov/vuln/detail/CVE-2026-11856
