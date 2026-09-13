# [H] Unbounded Memory Growth in QUIC Server Incoming Channel Queue

## Summary
Severity: High
Advisory: CVE-2026-14456
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-14456
Type: osv

## Details
Issue summary: When an OpenSSL QUIC server (Listener SSL object) processes
valid QUIC Initial packets for unknown destination connection IDs, it
can allocate and queue new incoming channels without enforcing any limit.

Impact summary: A remote peer that can make many Initial packets reach the
server listener faster than the application accepts connections, can cause the
memory allocated to store the per-channel state to grow without any limits,
potentially making the QUIC listener unavailable and causing Denial of Service.

CWE: CWE-770: Allocation of Resources Without Limits or Throttling

Description: The function that handles inbound QUIC packets uses
Connection-Id from the packet header to find an existing connection
(QUIC channel). If no existing connection is found and the packet
type is INITIAL, the function treats the packet as a new connection. It
allocates a new channel object and inserts it into a queue where it
waits to be accepted by the local application with SSL_accept(3ossl).
The memory occupied by these initial channel objects may grow
without bounds if the application is not able to call SSL_accept()
frequently enough to serve these inbound connection requests.

The issue is present since OpenSSL 3.5 when the QUIC server implementation
was added.

The fix introduces a limit for pending connections. The default limit is set
to 256 pending connections (waiting to be accepted by the local application).
Applications may change the default by calling SSL_set_value_uint(3ossl).

FIPS impact: no
The FIPS module is not affected as the QUIC implementation is outside of
the OpenSSL FIPS module boundary.

## References
- http://www.openwall.com/lists/oss-security/2026/08/13/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14456.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-14456
- https://openssl-library.org/news/secadv/20260813.txt
- https://github.com/openssl/openssl/commit/08e7756c3900bcfd77a720e7b74e27d6e4ed01a9
- https://github.com/openssl/openssl/commit/4084152e040329ca0194c4c1750b9b46d00a5b6b
- https://github.com/openssl/openssl/commit/f2f1465f2d2e5c61dfeac4d20fd093797d821139
