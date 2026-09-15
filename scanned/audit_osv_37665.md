# [H] CVE-2026-32665

## Summary
Severity: High
Advisory: CVE-2026-32665
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/CVE-2026-32665
Type: osv

## Details
In NLnet Labs Unbound 1.22.0 up to and including 1.25.1, when downstream DNS-over-QUIC (DoQ) is enabled, the first two bidirectional streams on a new QUIC connection (stream_id 0 and 4) bypass the per-stream 'quic-size' gate entirely, and large input buffers are allocated later, after only the 2-byte length prefix has been received from the initial streams. As a result, a remote client can make Unbound exceed the configured 'quic-size' limit with low-cost input. Using only one connection and two streams, each sending a declared 65535-byte length prefix and then holding the streams open, a client can already trivially make Unbound roughly allocate double that amount. This is a remote availability issue / memory-accounting bypass in the downstream DoQ implementation that leads to denial of service for new DoQ clients. This vulnerability needs Unbound to be compiled with DoQ support ('--with-libngtcp2') and the 'quic-port' to be configured for the listening interfaces.

## References
- https://www.nlnetlabs.nl/downloads/unbound/CVE-2026-32665.txt
