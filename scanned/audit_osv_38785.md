# [M] GnuTLS backend silently skips certificate chain verification when verify_peer is false

## Summary
Severity: Medium
Advisory: CVE-2026-42225
Aliases: GHSA-x2fv-6j6c-pxmx
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/CVE-2026-42225
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. Prior to version 2.17, on GnuTLS builds, the SIP TLS transport (sip_transport_tls) can accept connections with invalid or untrusted certificates even when the application explicitly enables certificate verification via verify_server = PJ_TRUE or verify_client = PJ_TRUE. This issue has been patched in version 2.17.

## References
- https://github.com/pjsip/pjproject/releases/tag/2.17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42225.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-x2fv-6j6c-pxmx
- https://nvd.nist.gov/vuln/detail/CVE-2026-42225
- https://github.com/pjsip/pjproject/commit/ef684252bb62b0716675b6e99ad7fe4c90e28920
