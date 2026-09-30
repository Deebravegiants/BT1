# [?] merge the fix of filter API deadlock from geth 1.10.8

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2021-11-08
Source: https://github.com/0xsoniclabs/sonic/commit/c42557dfccae9c2962bd8eb6aea33b29217b4557
Type: security-commit

## Details
merge the fix of filter API deadlock from geth 1.10.8

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
