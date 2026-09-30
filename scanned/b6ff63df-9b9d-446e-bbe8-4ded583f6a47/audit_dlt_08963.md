# [?] fix peer panic from fabric/gossip/util (#5136)

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2025-02-08
Source: https://github.com/hyperledger/fabric/commit/fbc557fe275a9b40399a3c28f8d0234aa20ea2bc
Type: security-commit

## Details
fix peer panic from fabric/gossip/util (#5136)

Signed-off-by: Fedor Partanskiy <fedor.partanskiy@atme.com>

## Patch
### gossip/util/pubsub.go
```diff
@@ -97,10 +97,9 @@ func (ps *PubSub) Subscribe(topic string, ttl time.Duration) Subscription {
 		s = NewSet()
 		ps.subscriptions[topic] = s
 	}
-	ps.Unlock()
-
 	// Add the subscription
 	s.Add(sub)
+	ps.Unlock()
 
 	// When the timeout expires, remove the subscription
 	time.AfterFunc(ttl, func() {
```
