# [M] OCSP verification bypass with TLS session reuse

## Summary
Severity: Medium
Advisory: CVE-2024-0853
Aliases: CURL-CVE-2024-0853
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-02-03
Source: https://osv.dev/vulnerability/CVE-2024-0853
Type: osv

## Details
curl inadvertently kept the SSL session ID for connections in its cache even when the verify status (*OCSP stapling*) test failed. A subsequent transfer to
the same hostname could then succeed if the session ID cache was still fresh, which then skipped the verify status check.

## References
- https://curl.se/docs/CVE-2024-0853.html
- https://curl.se/docs/CVE-2024-0853.json
- https://hackerone.com/reports/2298922
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0853.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0853
- https://security.netapp.com/advisory/ntap-20240307-0004/
- https://security.netapp.com/advisory/ntap-20240426-0009/
- https://security.netapp.com/advisory/ntap-20240503-0012/
