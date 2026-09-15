# [M] Improper Validation of OCSP Response During Outbound TLS Handshake Leading to Process Termination

## Summary
Severity: Medium
Advisory: BIT-mongodb-2026-13070
Aliases: CVE-2026-13070
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13070
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
A MongoDB server initiating an outbound TLS connection may terminate abnormally when processing a malformed OCSP response from a remote peer during the TLS handshake. OCSP stapling validation is enabled by default for outgoing TLS connections. Affected scenarios require the remote peer to hold a certificate issued by the cluster's trusted certificate authority, or for the connection to traverse an untrusted network path.

## References
- https://jira.mongodb.org/browse/SERVER-128362
- https://nvd.nist.gov/vuln/detail/CVE-2026-13070
