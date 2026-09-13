# [H] ALPINE-CVE-2026-14456

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-14456
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-14456
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=0 <3.5.8-r0
- Alpine:v3.23: `openssl` — affected >=0 <3.5.8-r0
- Alpine:v3.24: `openssl` — affected >=0 <3.5.8-r0

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
- https://security.alpinelinux.org/vuln/CVE-2026-14456
