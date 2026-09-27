# [H] QUIC Server May Trigger Double Free When Processing INITIAL Packet

## Summary
Severity: High
Advisory: CVE-2026-18798
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-18798
Type: osv

## Details
Issue summary: QUIC server may double free QRX (QUIC record layer RX) object
when channel creation fails for initial packet.

Impact summary: Double free leads to heap corruption, which typically results in 
termination of QUIC server process, leading to Denial of Service. There is so
far no evidence that this double free is exploitable for remote code execution,
thus it is considered highly improbable.

CWE: CWE-415: Double Free

Description: In order to validate initial packet, OpenSSL QUIC stack default
packet handler (port_default_packet_handler()) creates a so-called QRX object.
If the initial packet validates successfully with QRX object, the default packet
handler proceeds to channel (connection object) creation. The QRX object used
for packet validation is passed to port_bind_channel(), so it becomes part of
the newly created connection. If port_bind_channel() fails, then it also frees
the QRX object. Once port_bind_channel() returns, the port_default_packet_handler()
detects the failure and proceeds to the error branch, where the same QRX object is
freed for the second time.

The failure in port_bind_channel() function can be induced with a relatively
low effort by a malformed (non RFC 9000 compliant) INITIAL packet. If the packet
carries DCID (destination connection ID) which is shorter than 8 bytes, then
port_bind_channel() jumps to the error path after ossl_quic_lcidm_enrol_odcid()
detects that the DCID has invalid length.

FIPS impact: no
The FIPS module is not affected, as the QUIC implementation is outside of
the OpenSSL FIPS module boundary.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18798.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18798
- https://openssl-library.org/news/secadv/20260825.txt
- https://github.com/openssl/openssl/commit/70cebd74d3592f5272945501b58a60374c4e13af
- https://github.com/openssl/openssl/commit/967582d5037f01a26b6d19beae19af62a1b15c3c
- https://github.com/openssl/openssl/commit/a14a1deac403522fbeafabcb198503cf6caa7dc4
