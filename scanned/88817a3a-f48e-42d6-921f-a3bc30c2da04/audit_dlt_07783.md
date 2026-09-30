# [?] Fix TestNodeHealth_Concurrently race condition (#14033)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2024-05-22
Source: https://github.com/OffchainLabs/prysm/commit/4d190c41cc4f5ab269ec06cd047d5615d7d57b78
Type: security-commit

## Details
Fix TestNodeHealth_Concurrently race condition (#14033)

## Patch
### api/client/beacon/health.go
```diff
@@ -36,19 +36,19 @@ func (n *NodeHealthTracker) IsHealthy() bool {
 }
 
 func (n *NodeHealthTracker) CheckHealth(ctx context.Context) bool {
-	n.RLock()
+	n.Lock()
+	defer n.Unlock()
+
 	newStatus := n.node.IsHealthy(ctx)
 	if n.isHealthy == nil {
 		n.isHealthy = &newStatus
 	}
-	isStatusChanged := newStatus != *n.isHealthy
-	n.RUnlock()
 
+	isStatusChanged := newStatus != *n.isHealthy
 	if isStatusChanged {
-		n.Lock()
-		// Double-check the condition to ensure it hasn't changed since the first check.
+		// Update the health status
 		n.isHealthy = &newStatus
-		n.Unlock() // It's better to unlock as soon as the protected section is over.
+		// Send the new status to the health channel
 		n.healthChan <- newStatus
 	}
 	return newStatus
```

### api/client/beacon/health_test.go
```diff
@@ -99,9 +99,9 @@ func TestNodeHealth_Concurrency(t *testing.T) {
 	for i := 0; i < numGoroutines; i++ {
 		go func() {
 			defer wg.Done()
-			client.EXPECT().IsHealthy(gomock.Any()).Return(false)
+			client.EXPECT().IsHealthy(gomock.Any()).Return(false).Times(1)
 			n.CheckHealth(context.Background())
-			client.EXPECT().IsHealthy(gomock.Any()).Return(true)
+			client.EXPECT().IsHealthy(gomock.Any()).Return(true).Times(1)
 			n.CheckHealth(context.Background())
 		}()
 	}
```
