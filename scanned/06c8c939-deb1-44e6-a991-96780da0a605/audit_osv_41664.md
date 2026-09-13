# [H] QUIC ACK-only Packet Retention Can Cause Memory Exhaustion

## Summary
Severity: High
Advisory: CVE-2026-63075
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-63075
Type: osv

## Details
Issue summary: When OpenSSL processes QUIC traffic from a peer that repeatedly
sends ack-eliciting packets while not acknowledging ACK-only responses, the
QUIC stack can retain ACK-only packet metadata for the lifetime of the
connection.

Impact summary: A remote peer that can complete a QUIC handshake can
cause connection-scoped memory growth which may lead to Denial of Service
through memory exhaustion, especially with sustained traffic or many concurrent
QUIC connections.

CWE: CWE-770: Allocation of Resources Without Limits or Throttling

Description: When the OpenSSL QUIC stack sends an ACK-only packet,
there is no requirement by the QUIC protocol that the peer will acknowledge
that ACK-only packet (i.e. it is itself not ack-eliciting). However, the OpenSSL
implementation stores the metadata about the ACK frames regardless.
In and of itself that's ok, but if a malicious peer establishes a connection, and
then drives the connection such that ACK-only packets are forced from the 
OpenSSL implementation peer (i.e., by sending numerous PING frames),
and then withholding any subsequent acks for ack-eliciting data, like
legitimate data, said malicious peer can force inappropriate memory growth
on the OpenSSL peer, potentially leading to a Denial of Service.

The fix is to ensure that we account for the transmission of the ACK-only
packet in the packet histories high and low watermark without actually storing
the ACK-only packet metadata itself.

FIPS impact: no
The OpenSSL FIPS module is not affected as the QUIC code is
outside the FIPS module boundary.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63075.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63075
- https://openssl-library.org/news/secadv/20260825.txt
- https://github.com/openssl/openssl/commit/7308946576b12e64b8be53bcf0a120354b2b42bc
- https://github.com/openssl/openssl/commit/7c98d79738549df92868e7dd9be4bbf061eed709
- https://github.com/openssl/openssl/commit/bf84721c2548351176e367e6de505792f0118dc6
- https://github.com/openssl/openssl/commit/c902e5f16d6a9e130e96d3ca6d8f64d71652e393
