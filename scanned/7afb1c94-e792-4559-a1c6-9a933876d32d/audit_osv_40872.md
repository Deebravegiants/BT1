# [H] TLS 1.2 and DTLS client accepts unoffered anonymous cipher suite, bypassing server authentication

## Summary
Severity: High
Advisory: CVE-2026-55953
Aliases: EEF-CVE-2026-55953, GHSA-c6cw-pr89-w882
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-55953
Type: osv

## Details
The Erlang/OTP ssl TLS 1.2 (and earlier) and DTLS client does not verify that the cipher suite selected by the server in ServerHello was among the suites offered by the client in ClientHello. The client-side tls_handshake:hello/5 handler validates the negotiated protocol version and the downgrade sentinel but hands the server-chosen suite directly to ssl_handshake:handle_server_hello_extensions/9, which installs it without a membership check. The TLS 1.3 client path performs this check (per RFC 8446), so it is not affected.

An on-path attacker between the client and the intended server can respond with a ServerHello selecting an anonymous key exchange suite such as TLS_DH_anon_* or TLS_ECDH_anon_* that the client never offered. Anonymous suites do not require the server to present a certificate, so the entire verify_peer and cacerts configuration is bypassed: the attacker completes the handshake with its own ephemeral parameters, no certificate is validated, no hostname is checked, and ssl:connect returns {ok, Socket}. All subsequent application traffic is readable and modifiable by the attacker.

This issue affects OTP from OTP 17.0 before OTP 27.3.4.15, from OTP 28.0 before OTP 28.5.0.4, and from OTP 29.0 before OTP 29.0.4, corresponding to ssl from 5.3.4 before 11.2.12.11, from 11.3 before 11.6.0.4, and from 11.7 before 11.7.4. Whether OTP before OTP 17.0, corresponding to ssl before 5.3.4, is affected is unknown.

## References
- https://cna.erlef.org/cves/CVE-2026-55953.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-55953
- https://www.erlang.org/doc/system/versions.html#order-of-versions
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55953.json
- https://github.com/erlang/otp/security/advisories/GHSA-c6cw-pr89-w882
- https://nvd.nist.gov/vuln/detail/CVE-2026-55953
- https://github.com/erlang/otp/commit/064e236414614f9085cbbbd6eacf0e43c02d1b4b
- https://github.com/erlang/otp/commit/0a82596d425abe43dc2e0b3d74aa1557ef74051c
- https://github.com/erlang/otp/commit/e6ff938116b2872bccc478af7fefb56627285b77
- https://github.com/erlang/otp
