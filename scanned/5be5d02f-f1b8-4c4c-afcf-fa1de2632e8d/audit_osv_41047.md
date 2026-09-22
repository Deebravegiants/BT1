# [H] PJSIP: Stack overflow parsing a TLS peer certificate's SubjectAltName in GnuTLS backend

## Summary
Severity: High
Advisory: CVE-2026-57163
Aliases: GHSA-jm2j-6rg6-qvwx
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-57163
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. Prior to commit c4a151a, a stack buffer overflow exists in the GnuTLS TLS backend when parsing the Subject Alternative Name extension of a peer certificate (tls_cert_get_info() in ssl_sock_gtls.c). Only GnuTLS builds are affected (--with-gnutls); OpenSSL and Apple SecureTransport/Network.framework builds are not affected. While extracting certificate information after a TLS handshake, an incorrect buffer-size value can cause an oversized SubjectAltName entry to be written past the end of a fixed-size stack buffer. A network-positioned attacker presenting a crafted certificate — a malicious server to a connecting client, or a malicious client to a server that requests certificates — can trigger this during the TLS handshake, before any SIP-level authentication. Impact may range from unexpected application termination to control flow hijack/memory corruption. This issue has been patched via commit c4a151a.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57163.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-jm2j-6rg6-qvwx
- https://nvd.nist.gov/vuln/detail/CVE-2026-57163
- https://github.com/pjsip/pjproject/commit/c4a151af86fadd16d9480b2603eeb2abf4fb4f78
