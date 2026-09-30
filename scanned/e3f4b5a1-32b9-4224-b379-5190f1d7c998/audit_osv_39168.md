# [H] Deskflow: TLS multiplexer DoS on failed `SSL_accept`

## Summary
Severity: High
Advisory: CVE-2026-44296
Aliases: GHSA-3mxm-cgh2-6448
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-44296
Type: osv

## Details
Deskflow is a keyboard and mouse sharing app. Prior to 1.26.0.167, a remote, unauthenticated denial of service (DoS) vulnerability affects Deskflow servers running with TLS enabled (the default). When any TCP peer connects to the listening port and its first bytes do not parse as a valid TLS ClientHello, SecureSocket::secureAccept enters its fatal-error branch and calls Arch::sleep(1) (a blocking 1-second sleep) on the multiplexer worker thread. That thread services every socket on the server, including established TLS clients delivering mouse motion, keyboard events, and clipboard updates. A single failed handshake therefore stalls input delivery to all connected screens for ~1 second, and a sustained drip of malformed connections (≥ 1/s) makes the server effectively unusable while the attack persists. This vulnerability is fixed in 1.26.0.167.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44296.json
- https://github.com/deskflow/deskflow/security/advisories/GHSA-3mxm-cgh2-6448
- https://nvd.nist.gov/vuln/detail/CVE-2026-44296
- https://github.com/deskflow/deskflow/commit/329783490bd16774ba903b84212467d20d76bfba
