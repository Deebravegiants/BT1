# [?] p2p: fix nil pointer crash with --nodiscover (#19055)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-02-12
Source: https://github.com/erigontech/erigon/commit/a4d45814af5a2a538a7ad9b346b99dfc4a040eb0
Type: security-commit

## Details
p2p: fix nil pointer crash with --nodiscover (#19055)

- Fix nil pointer dereference in `setupDialScheduler` when running with
`--nodiscover`
- `cmp.Or[nodeResolver](srv.discv5, srv.discv4)` wraps nil concrete
pointers (`*discover.UDPv5`, `*discover.UDPv4`) into non-nil interface
values (Go nil interface trap), causing a crash at `v5_udp.go:222` when
`Resolve()` is called
- Replace with explicit nil checks so the resolver stays nil when
discovery is disabled

## Patch
### p2p/server.go
```diff
@@ -22,7 +22,6 @@ package p2p
 
 import (
 	"bytes"
-	"cmp"
 	"context"
 	"crypto/ecdsa"
 	"encoding/hex"
@@ -597,7 +596,13 @@ func (srv *Server) setupDialScheduler() {
 		dialer:         srv.Dialer,
 		clock:          srv.clock,
 	}
-	config.resolver = cmp.Or[nodeResolver](srv.discv5, srv.discv4)
+	// NOTE: cmp.Or cannot be used here because wrapping a nil concrete pointer
+	// in an interface produces a non-nil interface value (Go nil interface trap).
+	if srv.discv5 != nil {
+		config.resolver = srv.discv5
+	} else if srv.discv4 != nil {
+		config.resolver = srv.discv4
+	}
 	if config.dialer == nil {
 		config.dialer = tcpDialer{&net.Dialer{Timeout: defaultDialTimeout}}
 	}
```
