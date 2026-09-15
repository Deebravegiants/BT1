# [H] TCPDF missing certificate validation

## Summary
Severity: High
Advisory: GHSA-9mgx-552f-59p6
CVE: CVE-2024-56521
CWE: CWE-295
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-12-27
Source: https://github.com/advisories/GHSA-9mgx-552f-59p6
Type: github-advisory

## Affected
- Packagist: `tecnickcom/tcpdf` — affected >=0 <6.8.0

## Details
An issue was discovered in TCPDF before 6.8.0. If libcurl is used, CURLOPT_SSL_VERIFYHOST and CURLOPT_SSL_VERIFYPEER are set unsafely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-56521
- https://github.com/tecnickcom/TCPDF/commit/aab43ab0a824e956276141a28a24c7c0be20f554
- https://github.com/tecnickcom/TCPDF
- https://github.com/tecnickcom/TCPDF/compare/6.7.8...6.8.0
- https://tcpdf.org
