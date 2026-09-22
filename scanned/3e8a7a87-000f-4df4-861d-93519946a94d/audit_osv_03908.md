# [H] ALPINE-CVE-2026-63075

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-63075
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-63075
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=0 <3.5.8-r0
- Alpine:v3.23: `openssl` — affected >=0 <3.5.8-r0
- Alpine:v3.24: `openssl` — affected >=0 <3.5.8-r0

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
- https://security.alpinelinux.org/vuln/CVE-2026-63075
