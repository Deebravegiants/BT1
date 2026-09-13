# [C] FreeRDP before 3.29.0 Improper Certificate Hostname Validation

## Summary
Severity: Critical
Advisory: CVE-2026-67293
Aliases: GHSA-5wr6-8m8j-3h7f
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-67293
Type: osv

## Details
FreeRDP before 3.29.0 (affected versions <= 3.28.0) contains an improper certificate hostname validation vulnerability. The TLS hostname matcher (tls_match_hostname() in libfreerdp/crypto/tls.c) treats a wildcard pattern such as *.example.com as matching any hostname ending in .example.com, so it incorrectly accepts a wildcard certificate for multi-label subdomains like a.b.example.com (which OpenSSL's X509_check_host() rejects). This weakens TLS server authentication under wildcard-certificate conditions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67293.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-5wr6-8m8j-3h7f
- https://nvd.nist.gov/vuln/detail/CVE-2026-67293
- https://www.vulncheck.com/advisories/freerdp-before-improper-certificate-hostname-validation
- https://github.com/FreeRDP/FreeRDP/commit/f3b4347105114fe7453828736bea069999af319f
