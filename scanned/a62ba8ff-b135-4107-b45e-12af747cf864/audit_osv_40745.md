# [H] Excessive Memory Use Buffering DTLS Records for a Future Epoch

## Summary
Severity: High
Advisory: CVE-2026-54874
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-54874
Type: osv

## Details
Issue summary: Receiving a DTLS record for a future epoch while a handshake
is in progress causes OpenSSL to buffer far more memory than the record
itself requires.

Impact summary: A peer can use a small amount of network traffic to make an
OpenSSL DTLS endpoint retain a disproportionately large amount of memory,
which may lead to a Denial of Service.

CWE: CWE-405: Asymmetric Resource Consumption (Amplification)

Description: While a DTLS handshake is in progress, a peer may legitimately
have already moved on to the next epoch (for example, having sent its
ChangeCipherSpec and Finished messages) before the local endpoint has
processed the same transition, typically because of reordering on the
underlying UDP transport. OpenSSL buffers such early records so that they
can be processed once the local endpoint catches up.

Buffering a record currently retains the entire read buffer it arrived in,
which is sized to hold the largest possible DTLS record (around 16
kilobytes), rather than just the bytes that make up the record itself. Up
to 100 such records may be buffered per connection. As a result, a peer
that sends a stream of small forged records claiming to belong to the next
epoch can cause an OpenSSL DTLS endpoint to retain around 1.7 megabytes of
memory, despite sending only a small fraction of that amount of data over
the network.

An attacker therefore gains a memory amplification factor of around 1200,
and can multiply the effect across as many associations as it is able to
open, making this a remote memory exhaustion Denial of Service risk for
DTLS servers. Since the memory retained per connection remains bounded,
and any limit an application already places on the number of concurrent
associations also bounds the total exposure, this issue has been assessed
as Low severity.

FIPS impact: no

No FIPS modules are affected by this issue as the affected code is outside
the OpenSSL FIPS module boundary.

OpenSSL 4.0, 3.6, 3.5, 3.4, 3.0, 1.1.1 and 1.0.2 are vulnerable to this
issue.

OpenSSL 4.0 users should upgrade to OpenSSL 4.0.2.
OpenSSL 3.6 users should upgrade to OpenSSL 3.6.4.
OpenSSL 3.5 users should upgrade to OpenSSL 3.5.8.
OpenSSL 3.4 users should upgrade to OpenSSL 3.4.7.
OpenSSL 3.0 users should upgrade to OpenSSL 3.0.22.

Premium support customers only:
OpenSSL 1.1.1 users should upgrade to OpenSSL 1.1.1zi
OpenSSL 1.0.2 users should upgrade to OpenSSL 1.0.2zr

This issue was reported on 18 May 2026 by Amazon Web Services.
The fix has been developed by Matt Caswell.

-- cut (non-publishing metadata for internal use) --
Reported by: Amazon Web Services
Fixed by: Matt Caswell

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54874.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-54874
- https://openssl-library.org/news/secadv/20260825.txt
- https://github.com/openssl/openssl/commit/4808b5d64176451f3d93d87d0ac9c81a9b13fb23
- https://github.com/openssl/openssl/commit/7110cb2f75806d0bf809eb2f90790d477900be40
- https://github.com/openssl/openssl/commit/a0c8ec557d9cac078f032d76cdf684fe743eb382
- https://github.com/openssl/openssl/commit/cc0c6710917cd5eec001b297355d2ba723505107
- https://github.com/openssl/openssl/commit/f52ffc11b90737ac89083909618dc2e1f42c561c
