# [?] fix: thor exits with panic (#1500)

## Summary
Severity: Unknown
Chain: VeChain
Component: vechain/thor
Published: 2025-11-27
Source: https://github.com/vechain/thor/commit/693ad1b3f17be9f19a67a4188e5018786421f99a
Type: security-commit

## Details
fix: thor exits with panic (#1500)

## Patch
### p2p/server.go
```diff
@@ -559,7 +559,6 @@ func (srv *Server) startListening() error {
 		srv.loopWG.Go(
 			func() {
 				nat.Map(srv.NAT, srv.quit, "tcp", laddr.Port, laddr.Port, "ethereum p2p")
-				srv.loopWG.Done()
 			})
 	}
 	return nil
```
