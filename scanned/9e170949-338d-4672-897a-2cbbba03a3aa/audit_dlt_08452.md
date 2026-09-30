# [?] fix(p2p/discovery,core/listener): fix timer deadlock (#4231)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2025-04-22
Source: https://github.com/celestiaorg/celestia-node/commit/7af0c47a25ab892d0f3da867c912496ebf6db137
Type: security-commit

## Details
fix(p2p/discovery,core/listener): fix timer deadlock (#4231)

## Patch
### core/listener.go
```diff
@@ -156,10 +156,6 @@ func (cl *Listener) listen(ctx context.Context, sub <-chan types.EventDataSigned
 					"hash", b.Header.Hash().String(),
 					"err", err)
 			}
-
-			if !timeout.Stop() {
-				<-timeout.C
-			}
 		case <-timeout.C:
 			cl.metrics.subscriptionStuck(ctx)
 			log.Error("underlying subscription is stuck")
```

### share/shwap/p2p/discovery/discovery.go
```diff
@@ -189,24 +189,16 @@ func (d *Discovery) Advertise(ctx context.Context) {
 
 			// we don't want retry indefinitely in busy loop
 			// internal discovery mechanism may need some time before attempts
-			errTimer := time.NewTimer(retryTimeout)
+			errTimer := time.After(retryTimeout)
 			select {
-			case <-errTimer.C:
-				errTimer.Stop()
-				if !timer.Stop() {
-					<-timer.C
-				}
+			case <-errTimer:
 				continue
 			case <-ctx.Done():
-				errTimer.Stop()
 				return
 			}
 		}
 
 		log.Infof("successfully advertised to topic %s", d.topic)
-		if !timer.Stop() {
-			<-timer.C
-		}
 		timer.Reset(d.params.AdvertiseInterval)
 		select {
 		case <-timer.C:
```
