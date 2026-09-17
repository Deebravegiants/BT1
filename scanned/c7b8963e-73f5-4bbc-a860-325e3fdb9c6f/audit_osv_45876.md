# [M] libcurl accidentally skips the certificate verification for QUIC connections when connecting to a...

## Summary
Severity: Medium
Advisory: JLSEC-2026-432
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-432
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.9.0+0 <8.14.1+0
- Julia: `LibCURL_jll` — affected >=8.8.0+0 <8.14.1+0

## Details
libcurl accidentally skips the certificate verification for QUIC connections when connecting to a host specified as an IP address in the URL. Therefore, it does not detect impostors or man-in-the-middle attacks.

## References
- http://www.openwall.com/lists/oss-security/2025/05/28/4
- https://curl.se/docs/CVE-2025-4947.html
- https://curl.se/docs/CVE-2025-4947.json
- https://github.com/advisories/GHSA-ppfq-jg49-mqj4
- https://hackerone.com/reports/3150884
- https://nvd.nist.gov/vuln/detail/CVE-2025-4947
