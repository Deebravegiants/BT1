# [?] les: fix channel assignment data race (#15441)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2017-11-09
Source: https://github.com/celo-org/celo-blockchain/commit/7ace02398160fe4d0f0bf9e7c49ff86e6fdb15bc
Type: security-commit

## Details
les: fix channel assignment data race (#15441)

## Patch
### les/serverpool.go
```diff
@@ -145,15 +145,15 @@ func (pool *serverPool) start(server *p2p.Server, topic discv5.Topic) {
 	pool.wg.Add(1)
 	pool.loadNodes()
 
-	go pool.eventLoop()
-
-	pool.checkDial()
 	if pool.server.DiscV5 != nil {
 		pool.discSetPeriod = make(chan time.Duration, 1)
 		pool.discNodes = make(chan *discv5.Node, 100)
 		pool.discLookups = make(chan bool, 100)
 		go pool.server.DiscV5.SearchTopic(pool.topic, pool.discSetPeriod, pool.discNodes, pool.discLookups)
 	}
+
+	go pool.eventLoop()
+	pool.checkDial()
 }
 
 // connect should be called upon any incoming connection. If the connection has been
```
