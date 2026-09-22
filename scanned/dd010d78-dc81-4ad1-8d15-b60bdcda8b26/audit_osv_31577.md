# [M] OpenSSL partial chain store policy bypass

## Summary
Severity: Medium
Advisory: CVE-2025-14819
Aliases: CURL-CVE-2025-14819
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/CVE-2025-14819
Type: osv

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
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14819.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-14819
