# [?] p2p/test/reconnect: fixed race condition

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2015-01-20
Source: https://github.com/libp2p/go-libp2p/commit/e77e4b1357eca1002eaf80cb03fb2e065e232829
Type: security-commit

## Details
p2p/test/reconnect: fixed race condition

## Patch
### test/reconnects/reconnect_test.go
```diff
@@ -188,16 +188,16 @@ func SubtestConnSendDisc(t *testing.T, hosts []host.Host) {
 			defer wg.Done()
 
 			go sF(s)
-			log.Debugf("getting handle %d", i)
+			log.Debugf("getting handle %d", j)
 			sc := <-ss // wait to get handle.
-			log.Debugf("spawning worker %d", i)
+			log.Debugf("spawning worker %d", j)
 
-			for i := 0; i < numMsgs; i++ {
+			for k := 0; k < numMsgs; k++ {
 				sc.send <- struct{}{}
 				<-sc.sent
-				log.Debugf("%d sent %d", j, i)
+				log.Debugf("%d sent %d", j, k)
 				<-sc.read
-				log.Debugf("%d read %d", j, i)
+				log.Debugf("%d read %d", j, k)
 			}
 			sc.close_ <- struct{}{}
 			<-sc.closed
```
