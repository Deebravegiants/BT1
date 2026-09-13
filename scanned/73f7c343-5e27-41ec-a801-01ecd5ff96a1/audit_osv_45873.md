# [M] When doing TLS related transfers with reused easy or multi handles and altering the...

## Summary
Severity: Medium
Advisory: JLSEC-2026-429
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-429
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.5.0+0 <8.20.0+0
- Julia: `LibCURL_jll` — affected >=7.87.0+0 <8.18.0+0

## Details
When doing TLS related transfers with reused easy or multi handles and
altering the  `CURLSSLOPT_NO_PARTIALCHAIN` option, libcurl could accidentally
reuse a CA store cached in memory for which the partial chain option was
reversed. Contrary to the user's wishes and expectations. This could make
libcurl find and accept a trust chain that it otherwise would not.

## References
- http://www.openwall.com/lists/oss-security/2026/01/07/5
- https://curl.se/docs/CVE-2025-14819.html
- https://curl.se/docs/CVE-2025-14819.json
- https://github.com/advisories/GHSA-vqhr-m87q-9jqh
- https://nvd.nist.gov/vuln/detail/CVE-2025-14819
