# [H] CoreDNS has TSIG authentication bypass on DoT, DoH, DoH3, DoQ, and gRPC

## Summary
Severity: High
Advisory: GHSA-qhmp-q7xh-99rh
CVE: CVE-2026-33190
CWE: CWE-287, CWE-303
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-qhmp-q7xh-99rh
Type: github-advisory

## Affected
- Go: `github.com/coredns/coredns` — affected >=0 <1.14.3

## Details
### Summary
CoreDNS' tsig plugin can be bypassed on non-plain-DNS transports because it trusts the transport writer's TsigStatus() instead of performing verification itself. In the attached PoC, plain DNS/TCP correctly rejects an invalid TSIG (NOTAUTH), while the same invalid-TSIG request is accepted over DoT (tls://) and DoH (https://), allowing a client without the shared secret to satisfy require all. The same bug class affects DoH3, DoQ, and gRPC.

### Details
The tsig plugin decides whether an incoming TSIG was valid by consulting w.TsigStatus(): tsigStatus := w.TsigStatus(); if tsigStatus != nil { ... NOTAUTH ... } (plugin/tsig/tsig.go)

Two affected transports are shown directly in the PoC:
- DoH: DoHWriter.TsigStatus() always returns nil (core/dnsserver/https.go), and the HTTP server passes unpacked DNS messages directly into the plugin chain.
- DoT: the TLS server builds a dns.Server without setting TsigSecret (core/dnsserver/server_tls.go), unlike plain DNS/TCP/UDP which sets TsigSecret: s.tsigSecret (core/dnsserver/server.go).

The same transport-family bug pattern also appears on other transports:
- DoH3 reuses the DoH writer path (core/dnsserver/server_https3.go -> core/dnsserver/https.go), so it inherits the same TsigStatus() == nil behavior.
- DoQ uses DoQWriter.TsigStatus() error { return nil } (core/dnsserver/quic.go).
- gRPC uses gRPCresponse.TsigStatus() error { return nil } (core/dnsserver/server_grpc.go).

The attached PoC was kept deliberately small (baseline TCP+DoT+DoH only) for convenience.

### PoC
1. Adjust COREDNS_BIN in the PoC to point at right path (see the top-level const definitions for tunables as well)
2. Run python3 ./tsig-repro.py
3. Expected output:
*** Start CoreDNS ***
Corefile: /tmp/vh-f001-tsig-doh-dot-bypass/Corefile
Log: /tmp/vh-f001-tsig-doh-dot-bypass/coredns.log

*** Baseline (plain TCP) ***
no_tsig rcode=5 (expected REFUSED=5)
invalid_tsig rcode=9 (expected NOTAUTH=9)

*** Candidate (DoT) ***
no_tsig rcode=5 (expected REFUSED=5)
invalid_tsig rcode=0 ancount=1 (expected NOERROR=0 and ancount>0)

*** Candidate (DoH) ***
no_tsig http=200 rcode=5 (expected REFUSED=5)
invalid_tsig http=200 rcode=0 ancount=1 (expected NOERROR=0 and ancount>0)

*** OK ***
TSIG bypass reproduced: plain TCP rejects invalid TSIG, while DoT and DoH accept it.
Results: /tmp/vh-f001-tsig-doh-dot-bypass/results.json


### Impact
Unauthenticated remote clients can bypass TSIG-based authentication/authorization on first-class encrypted transports, enabling access to whatever the deployment intended to restrict behind tsig { require all } (e.g., zone data/privileged queries, etc.).

## References
- https://github.com/coredns/coredns/security/advisories/GHSA-qhmp-q7xh-99rh
- https://nvd.nist.gov/vuln/detail/CVE-2026-33190
- https://github.com/coredns/coredns
- https://github.com/coredns/coredns/releases/tag/v1.14.3
