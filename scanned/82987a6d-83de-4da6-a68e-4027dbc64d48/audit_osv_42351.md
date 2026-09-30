# [C] FreeRDP before 3.29.0 TLS Certificate EKU Bypass

## Summary
Severity: Critical
Advisory: CVE-2026-67294
Aliases: GHSA-89c6-jjrw-96h4
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-67294
Type: osv

## Details
FreeRDP before 3.29.0 improperly validates the Extended Key Usage (EKU) purpose of the peer certificate during client-side server TLS authentication. In x509_utils_verify(), when server-purpose (X509_PURPOSE_SSL_SERVER) verification fails, the code falls back to client-purpose and any-purpose verification, so a trusted, hostname-matching certificate valid only for clientAuth can be accepted as the RDP server certificate. In environments relying on EKU separation between client and server certificates, this allows a clientAuth-only certificate issued by a trusted CA to bypass server certificate purpose validation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67294.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-89c6-jjrw-96h4
- https://nvd.nist.gov/vuln/detail/CVE-2026-67294
- https://www.vulncheck.com/advisories/freerdp-before-tls-certificate-eku-bypass
- https://github.com/FreeRDP/FreeRDP/commit/f3b4347105114fe7453828736bea069999af319f
