# [H] gzip integer overflow

## Summary
Severity: High
Advisory: CVE-2025-0725
Aliases: CURL-CVE-2025-0725
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-02-05
Source: https://osv.dev/vulnerability/CVE-2025-0725
Type: osv

## Details
When libcurl is asked to perform automatic gzip decompression of
content-encoded HTTP responses with the `CURLOPT_ACCEPT_ENCODING` option,
**using zlib 1.2.0.3 or older**, an attacker-controlled integer overflow would
make libcurl perform a buffer overflow.

## References
- http://www.openwall.com/lists/oss-security/2025/02/05/3
- http://www.openwall.com/lists/oss-security/2025/02/06/2
- http://www.openwall.com/lists/oss-security/2025/02/06/4
- https://curl.se/docs/CVE-2025-0725.html
- https://curl.se/docs/CVE-2025-0725.json
- https://hackerone.com/reports/2956023
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/0xxx/CVE-2025-0725.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-0725
- https://security.netapp.com/advisory/ntap-20250306-0009/
- https://github.com/curl/curl/commit/76f83f0db23846e254d940ec7
