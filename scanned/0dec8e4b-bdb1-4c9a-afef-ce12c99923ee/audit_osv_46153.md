# [M] TLS 1.3 post-handshake authentication (PHA) issue where a server could accept a client's Finished...

## Summary
Severity: Medium
Advisory: JLSEC-2026-737
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-737
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=5.7.2+0 <5.9.2+0

## Details
TLS 1.3 post-handshake authentication (PHA) issue where a server could accept a client's Finished message without the client having sent a Certificate and CertificateVerify. The post-handshake-auth exemption that allows an empty/absent peer certificate was only intended for the initial handshake, but it was also being applied while a post-handshake CertificateRequest was still outstanding. The check is now scoped to the initial handshake only: on the server, once a post-handshake CertificateRequest has been sent (certReqCtx is set), a peer certificate and a valid CertificateVerify are required again before the Finished is accepted, with empty-certificate handling following the configured verify mode (`FAIL_IF_NO_PEER_CERT`) just as during first-handshake client authentication. Only affects TLS 1.3 servers built with post-handshake authentication support (`WOLFSSL_POST_HANDSHAKE_AUTH` / --enable-postauth, included in --enable-all) that enable `WOLFSSL_VERIFY_POST_HANDSHAKE` and request a client certificate after the handshake via `wolfSSL_request_certificate()`. Clients, and servers that do not use post-handshake authentication, are unaffected.

## References
- https://github.com/advisories/GHSA-gq94-hf88-g4wv
- https://github.com/wolfSSL/wolfssl/pull/10702
- https://nvd.nist.gov/vuln/detail/CVE-2026-55962
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/
