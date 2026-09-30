# [M] TLS 1.3 post-handshake authentication: server accepts Finished without client Certificate/CertificateVerify

## Summary
Severity: Medium
Advisory: CVE-2026-55962
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-55962
Type: osv

## Details
TLS 1.3 post-handshake authentication (PHA) issue where a server could accept a client's Finished message without the client having sent a Certificate and CertificateVerify. The post-handshake-auth exemption that allows an empty/absent peer certificate was only intended for the initial handshake, but it was also being applied while a post-handshake CertificateRequest was still outstanding. The check is now scoped to the initial handshake only: on the server, once a post-handshake CertificateRequest has been sent (certReqCtx is set), a peer certificate and a valid CertificateVerify are required again before the Finished is accepted, with empty-certificate handling following the configured verify mode (FAIL_IF_NO_PEER_CERT) just as during first-handshake client authentication. Only affects TLS 1.3 servers built with post-handshake authentication support (WOLFSSL_POST_HANDSHAKE_AUTH / --enable-postauth, included in --enable-all) that enable WOLFSSL_VERIFY_POST_HANDSHAKE and request a client certificate after the handshake via wolfSSL_request_certificate(). Clients, and servers that do not use post-handshake authentication, are unaffected.

## References
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55962.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-55962
- https://github.com/wolfSSL/wolfssl/pull/10702
- https://github.com/wolfSSL/wolfssl
