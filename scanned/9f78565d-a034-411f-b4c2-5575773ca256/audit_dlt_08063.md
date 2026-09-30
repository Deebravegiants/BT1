# [?] p2p: fix rare deadlock in Stop (#17260)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2018-07-30
Source: https://github.com/celo-org/celo-blockchain/commit/8f4c4fea20da04557d94eab0acbbc681861cce15
Type: security-commit

## Details
p2p: fix rare deadlock in Stop (#17260)

## Patch
### p2p/server.go
```diff
@@ -340,8 +340,8 @@ func (srv *Server) makeSelf(listener net.Listener, ntab discoverTable) *discover
 // It blocks until all active connections have been closed.
 func (srv *Server) Stop() {
 	srv.lock.Lock()
-	defer srv.lock.Unlock()
 	if !srv.running {
+		srv.lock.Unlock()
 		return
 	}
 	srv.running = false
@@ -350,6 +350,7 @@ func (srv *Server) Stop() {
 		srv.listener.Close()
 	}
 	close(srv.quit)
+	srv.lock.Unlock()
 	srv.loopWG.Wait()
 }
 
```
