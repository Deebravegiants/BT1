# [?] go/runtime/committee: Fix crash in node selection policy

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2020-04-16
Source: https://github.com/oasisprotocol/oasis-core/commit/c6956182077c35d765690ea036f8fabc0fae026a
Type: security-commit

## Details
go/runtime/committee: Fix crash in node selection policy

There is a race condition where the committee client has been updated with new
connections, but the policy has not yet been as the client is not yet frozen.
This could previously lead to a panic in GetConnection but now correctly returns
nil.

## Patch
### go/runtime/committee/client.go
```diff
@@ -80,14 +80,19 @@ func (rr *roundRobinNodeSelectionPolicy) Pick() signature.PublicKey {
 }
 
 func (rr *roundRobinNodeSelectionPolicy) UpdatePolicy(feedback NodeSelectionFeedback) {
+	if feedback.Bad == nil {
+		// Don't rotate nodes if the feedback was good.
+		return
+	}
+
 	rr.Lock()
 	defer rr.Unlock()
 
 	if len(rr.nodes) == 0 {
 		return
 	}
 
-	// The round-robin policy ignores any feedback.
+	// The round-robin policy ignores any bad feedback.
 	rr.index = (rr.index + 1) % len(rr.nodes)
 }
 
@@ -233,7 +238,12 @@ func (cc *committeeClient) GetConnection() *grpc.ClientConn {
 	}
 
 	id := cc.nodeSelectionPolicy.Pick()
-	return cc.conns[id].conn
+	c := cc.conns[id]
+	if c == nil {
+		// Node selection policy may not have been updated yet.
+		return nil
+	}
+	return c.conn
 }
 
 func (cc *committeeClient) UpdateNodeSelectionPolicy(feedback NodeSelectionFeedback) {
```
