# [?] Merge pull request #182 from uprendis/feature/fix-filter-api-deadlock

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2021-11-09
Source: https://github.com/0xsoniclabs/sonic/commit/cac2ad3378a89155e3a528b4303c2aad2052f657
Type: security-commit

## Details
Merge pull request #182 from uprendis/feature/fix-filter-api-deadlock

Fix filter API deadlock

## Patch
### gossip/filters/api.go
```diff
@@ -84,28 +84,38 @@ func NewPublicFilterAPI(backend Backend, cfg Config) *PublicFilterAPI {
 		events:  NewEventSystem(backend),
 		filters: make(map[rpc.ID]*filter),
 	}
-	go api.timeoutLoop()
+	go api.timeoutLoop(5 * time.Minute)
 
 	return api
 }
 
-// timeoutLoop runs every 5 minutes and deletes filters that have not been recently used.
-// Tt is started when the api is created.
-func (api *PublicFilterAPI) timeoutLoop() {
-	ticker := time.NewTicker(5 * time.Minute)
+// timeoutLoop runs at the interval set by 'timeout' and deletes filters
+// that have not been recently used. It is started when the API is created.
+func (api *PublicFilterAPI) timeoutLoop(timeout time.Duration) {
+	var toUninstall []*Subscription
+	ticker := time.NewTicker(timeout)
+	defer ticker.Stop()
 	for {
 		<-ticker.C
 		api.filtersMu.Lock()
 		for id, f := range api.filters {
 			select {
 			case <-f.deadline.C:
-				f.s.Unsubscribe()
+				toUninstall = append(toUninstall, f.s)
 				delete(api.filters, id)
 			default:
 				continue
 			}
 		}
 		api.filtersMu.Unlock()
+
+		// Unsubscribes are processed outside the lock to avoid the following scenario:
+		// event loop attempts broadcasting events to still active filters while
+		// Unsubscribe is waiting for it to process the uninstall request.
+		for _, s := range toUninstall {
+			s.Unsubscribe()
+		}
+		toUninstall = nil
 	}
 }
 
```
