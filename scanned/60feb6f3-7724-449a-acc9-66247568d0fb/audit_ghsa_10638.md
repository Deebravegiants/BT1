# [H] CoreDNS' DoQ worker pool does not bound stream backlog

## Summary
Severity: High
Advisory: GHSA-2wpx-qpw2-g5h5
CVE: CVE-2026-32934
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-2wpx-qpw2-g5h5
Type: github-advisory

## Affected
- Go: `github.com/coredns/coredns` — affected >=0 <1.14.3

## Details
### Summary
CoreDNS' DNS-over-QUIC (DoQ) server can be driven into large goroutine and memory growth by a remote client that opens many QUIC streams and stalls after sending only 1 byte. Even with a small configured quic { worker_pool_size ... }, CoreDNS still spawns a goroutine per accepted stream (workers + waiters) and active workers can block indefinitely in io.ReadFull() with no per-stream read deadline, enabling unauthenticated remote DoS via memory exhaustion/OOM-kill.

### Details
CoreDNS' DoQ server uses a global worker pool (streamProcessPool) to limit concurrent stream processing, but when the pool is full it still spawns a goroutine per accepted stream that waits to acquire a worker token: select { case s.streamProcessPool <- ...: go ...; default: go ... wait for token ... } (core/dnsserver/server_quic.go)

Additionally, the DoQ message framing reads are blocking io.ReadFull() calls with no per-stream read deadline: readDOQMessage() reads the 2-byte length prefix and message body via io.ReadFull() (core/dnsserver/server_quic.go)

This allows an attacker to pin all workers by sending 1 byte (so io.ReadFull() blocks waiting for the second byte of the DoQ length prefix), while also creating an unbounded backlog of goroutines waiting for a worker token.

Note: this appears to be a result of an incomplete fix/regression for CVE-2025-47950 (GHSA-cvx7-x8pj-x2gw).

### PoC
1. Adjust COREDNS_BIN in the PoC to point at right path (see the top-level const definitions for tunables as well)
2. Run python3 ./doq-dos-repro.py
3. Expected sample output:
*** Start CoreDNS ***
Corefile: /tmp/vh-f003-doq-mem-regression/Corefile
Log: /tmp/vh-f003-doq-mem-regression/coredns.log

*** Baseline sample (idle) ***
rss_kib=49380 go_goroutines=17

*** Build + run partial-stream flooder ***
go: downloading golang.org/x/net v0.43.0
go: downloading golang.org/x/crypto v0.41.0
go: downloading go.uber.org/mock v0.5.2
go: downloading github.com/stretchr/testify v1.11.1
go: downloading golang.org/x/sys v0.35.0
go: downloading github.com/pmezard/go-difflib v1.0.0
go: downloading github.com/davecgh/go-spew v1.1.1
go: downloading gopkg.in/yaml.v3 v3.0.1

*** Candidate sample (during attack) ***
rss_kib=137968 go_goroutines=15557

*** Flooder output ***
opened conns=60 streams_per_conn=256 total_streams=15360

*** Wrote results ***
/tmp/vh-f003-doq-mem-regression/results.json

*** OK ***
DoQ flood caused goroutine/RSS growth despite worker_pool_size.


### Impact
Unauthenticated remote DoS on an encrypted DNS transport via goroutine/RSS growth leading to OOM-kill/crash and service outage.

## References
- https://github.com/coredns/coredns/security/advisories/GHSA-2wpx-qpw2-g5h5
- https://github.com/coredns/coredns/security/advisories/GHSA-cvx7-x8pj-x2gw
- https://nvd.nist.gov/vuln/detail/CVE-2026-32934
- https://github.com/coredns/coredns
- https://github.com/coredns/coredns/releases/tag/v1.14.3
