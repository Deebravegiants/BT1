# [M] libcurl supports *pinning* of the server certificate public key for HTTPS transfers

## Summary
Severity: Medium
Advisory: JLSEC-2026-433
Ecosystem: Julia
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-433
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.5.0+0 <8.14.1+0
- Julia: `LibCURL_jll` — affected >=8.5.0+0 <8.14.1+0

## Details
libcurl supports *pinning* of the server certificate public key for HTTPS transfers. Due to an omission, this check is not performed when connecting with QUIC for HTTP/3, when the TLS backend is wolfSSL. Documentation says the option works with wolfSSL, failing to specify that it does not for QUIC and HTTP/3. Since pinning makes the transfer succeed if the pin is fine, users could unwittingly connect to an impostor server without noticing.

## References
- http://www.openwall.com/lists/oss-security/2025/05/28/5
- https://curl.se/docs/CVE-2025-5025.html
- https://curl.se/docs/CVE-2025-5025.json
- https://github.com/advisories/GHSA-x8ch-h5vv-q6cm
- https://hackerone.com/reports/3153497
- https://nvd.nist.gov/vuln/detail/CVE-2025-5025
