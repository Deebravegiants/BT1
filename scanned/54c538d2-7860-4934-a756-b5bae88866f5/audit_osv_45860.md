# [M] libcurl skips the certificate verification for a QUIC connection under certain conditions, when...

## Summary
Severity: Medium
Advisory: JLSEC-2026-415
Ecosystem: Julia
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-415
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.6.0+0 <8.9.0+0
- Julia: `LibCURL_jll` — affected >=8.6.0+0 <8.7.1+0

## Details
libcurl skips the certificate verification for a QUIC connection under certain conditions, when built to use wolfSSL. If told to use an unknown/bad cipher or curve, the error path accidentally skips the verification and returns OK, thus ignoring any certificate problems.

## References
- http://seclists.org/fulldisclosure/2024/Jul/18
- http://seclists.org/fulldisclosure/2024/Jul/19
- http://seclists.org/fulldisclosure/2024/Jul/20
- http://www.openwall.com/lists/oss-security/2024/03/27/2
- https://curl.se/docs/CVE-2024-2379.html
- https://curl.se/docs/CVE-2024-2379.json
- https://github.com/advisories/GHSA-wr4c-gwg7-p734
- https://hackerone.com/reports/2410774
- https://nvd.nist.gov/vuln/detail/CVE-2024-2379
- https://security.netapp.com/advisory/ntap-20240531-0001
- https://security.netapp.com/advisory/ntap-20240531-0001/
- https://support.apple.com/kb/HT214118
- https://support.apple.com/kb/HT214119
- https://support.apple.com/kb/HT214120
