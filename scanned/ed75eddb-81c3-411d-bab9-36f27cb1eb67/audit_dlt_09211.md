# [?] fix weird race condition in goprocess that caused a few panics

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2015-02-20
Source: https://github.com/libp2p/go-libp2p/commit/83ea98ed5e06effba1636b39e34c4d8a5013dacf
Type: security-commit

## Details
fix weird race condition in goprocess that caused a few panics

## Patch
### net/swarm/swarm_dial.go
```diff
@@ -17,7 +17,6 @@ import (
 	ma "github.com/jbenet/go-ipfs/Godeps/_workspace/src/github.com/jbenet/go-multiaddr"
 	manet "github.com/jbenet/go-ipfs/Godeps/_workspace/src/github.com/jbenet/go-multiaddr-net"
 	process "github.com/jbenet/go-ipfs/Godeps/_workspace/src/github.com/jbenet/goprocess"
-	procctx "github.com/jbenet/go-ipfs/Godeps/_workspace/src/github.com/jbenet/goprocess/context"
 	ratelimit "github.com/jbenet/go-ipfs/Godeps/_workspace/src/github.com/jbenet/goprocess/ratelimit"
 )
 
@@ -384,7 +383,7 @@ func (s *Swarm) dialAddrs(ctx context.Context, d *conn.Dialer, p peer.ID, remote
 	// to end early.
 	go func() {
 		// rate limiting just in case. at most 10 addrs at once.
-		limiter := ratelimit.NewRateLimiter(procctx.WithContext(ctx), 10)
+		limiter := ratelimit.NewRateLimiter(process.Background(), 10)
 		limiter.Go(func(worker process.Process) {
 			// permute addrs so we try different sets first each time.
 			for _, i := range rand.Perm(len(remoteAddrs)) {
@@ -402,6 +401,9 @@ func (s *Swarm) dialAddrs(ctx context.Context, d *conn.Dialer, p peer.ID, remote
 				})
 			}
 		})
+
+		<-ctx.Done()
+		limiter.Close()
 	}()
 
 	// wair fot the results.
```
