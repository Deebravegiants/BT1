# [?] p2p: resolved deadlock on p2p server shutdown

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2024-01-25
Source: https://github.com/bnb-chain/bsc/commit/d49da4348c0796973f3e76b2d4fdf7a80e0289ea
Type: security-commit

## Details
p2p: resolved deadlock on p2p server shutdown

## Patch
### eth/handler.go
```diff
@@ -381,8 +381,6 @@ func (h *handler) protoTracker() {
 				<-h.handlerDoneCh
 			}
 			return
-		case <-h.stopCh:
-			return
 		}
 	}
 }
```

### eth/sync.go
```diff
@@ -132,8 +132,6 @@ func (cs *chainSyncer) loop() {
 				<-cs.doneCh
 			}
 			return
-		case <-cs.handler.stopCh:
-			return
 		}
 	}
 }
```

### p2p/server.go
```diff
@@ -65,9 +65,6 @@ const (
 
 	// Maximum amount of time allowed for writing a complete message.
 	frameWriteTimeout = 20 * time.Second
-
-	// Maximum time to wait before stop the p2p server
-	stopTimeout = 5 * time.Second
 )
 
 var (
@@ -448,18 +445,7 @@ func (srv *Server) Stop() {
 	}
 	close(srv.quit)
 	srv.lock.Unlock()
-
-	stopChan := make(chan struct{})
-	go func() {
-		srv.loopWG.Wait()
-		close(stopChan)
-	}()
-
-	select {
-	case <-stopChan:
-	case <-time.After(stopTimeout):
-		srv.log.Warn("stop p2p server timeout, forcing stop")
-	}
+	srv.loopWG.Wait()
 }
 
 // sharedUDPConn implements a shared connection. Write sends messages to the underlying connection while read returns
```
