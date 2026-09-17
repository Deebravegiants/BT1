# [C] QUIC has Broken TLS verification

## Summary
Severity: Critical
Advisory: GHSA-2r8v-p65x-3663
CVE: CVE-2026-49457
CWE: CWE-295, CWE-297
Ecosystem: Hex
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-2r8v-p65x-3663
Type: github-advisory

## Affected
- Hex: `quic` — affected >=0 <1.4.4

## Details
### Impact

The QUIC client did not authenticate the server during the TLS 1.3 handshake. The CertificateVerify signature was not checked, the certificate chain was not validated, and the hostname was not compared against the certificate, so `verify` was effectively a no-op on the client. A man-in-the-middle on the network path could present any certificate and impersonate any server, defeating the confidentiality and integrity of the connection. HTTP/3 uses the same client and was equally affected. Handshakes authenticated by a PSK (session resumption) are not affected, because the peer is authenticated by the PSK binder and no certificate is sent.

### Patches

Fixed in 1.4.4. The client now verifies the CertificateVerify signature, validates the certificate chain against the trust store (`cacerts` option, the operating system store by default), and checks the hostname. Client `verify` now defaults to on; set `verify => false` to accept any certificate (for example a self-signed test server).

### Workarounds

None before 1.4.4. `verify => true` had no effect, and inspecting the certificate after connecting does not help because without the signature check the peer is never proven to own the certificate it presents.

### Credit

Reported by benmmurphy.

## References
- https://github.com/benoitc/erlang_quic/security/advisories/GHSA-2r8v-p65x-3663
- https://github.com/benoitc/erlang_quic
