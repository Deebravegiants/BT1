# [C] FreeRDP before 3.29.0 TLS Certificate Identity Validation Bypass

## Summary
Severity: Critical
Advisory: CVE-2026-66402
Aliases: GHSA-43hh-p3vw-hfx3
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-66402
Type: osv

## Details
FreeRDP before 3.29.0 (affected versions <= 3.28.0) contains multiple TLS certificate identity validation weaknesses in tls_verify_certificate(), tls_match_hostname(), and x509_utils_get_dns_names(). Because FreeRDP performs custom Common Name and DNS SAN string matching instead of using OpenSSL's length-aware identity validation APIs, it (1) truncates DNS SAN values at embedded NUL bytes (accepting e.g. 'victim.example\0.attacker.example' as 'victim.example'), (2) accepts a matching Common Name even when non-matching DNS SAN entries are present, and (3) accepts IP-literal targets via DNS/CN matching without comparing iPAddress SANs. Under a trusted or misissued certificate chain, an attacker positioned to present such a certificate can bypass server identity verification, weakening TLS server authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66402.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-43hh-p3vw-hfx3
- https://nvd.nist.gov/vuln/detail/CVE-2026-66402
- https://www.vulncheck.com/advisories/freerdp-before-tls-certificate-identity-validation-bypass
- https://github.com/FreeRDP/FreeRDP/commit/b9533f07f98c25ed01c5f543b4d0ce73e120f5fd
