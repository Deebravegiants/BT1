# [M] curl inadvertently kept the SSL session ID for connections in its cache even when the verify status...

## Summary
Severity: Medium
Advisory: JLSEC-2026-412
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-412
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.5.0+0 <8.6.0+0
- Julia: `LibCURL_jll` — affected >=8.5.0+0 <8.6.0+0

## Details
curl inadvertently kept the SSL session ID for connections in its cache even when the verify status (*OCSP stapling*) test failed. A subsequent transfer to
the same hostname could then succeed if the session ID cache was still fresh, which then skipped the verify status check.

## References
- https://curl.se/docs/CVE-2024-0853.html
- https://curl.se/docs/CVE-2024-0853.json
- https://github.com/advisories/GHSA-697h-9h25-w4fm
- https://hackerone.com/reports/2298922
- https://nvd.nist.gov/vuln/detail/CVE-2024-0853
- https://security.netapp.com/advisory/ntap-20240307-0004
- https://security.netapp.com/advisory/ntap-20240307-0004/
- https://security.netapp.com/advisory/ntap-20240426-0009
- https://security.netapp.com/advisory/ntap-20240426-0009/
- https://security.netapp.com/advisory/ntap-20240503-0012
- https://security.netapp.com/advisory/ntap-20240503-0012/
